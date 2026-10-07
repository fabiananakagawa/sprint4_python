# Testes automatizados do ChargeGrid Intelligence (Sprint 4)
# Executar na raiz do repositório:  python -m unittest discover -s tests -v

import copy
import importlib.util
import os
import random
import sys
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

# o arquivo principal tem espaços no nome, então é carregado pelo caminho
_spec = importlib.util.spec_from_file_location("simulador", os.path.join(RAIZ, "Programa de Recarga GoodWe.py"))
sim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sim)
sim.VELOCIDADE = 0.0

import dashboard  # noqa: E402
import weely  # noqa: E402


def config_demo(seed=22):
	random.seed(seed)
	return sim.completar_configuracao(sim.configurar_automatico())


def silencioso(funcao, *args, **kwargs):
	original = sim.print if hasattr(sim, "print") else None
	sim.print = lambda *a, **k: None
	try:
		return funcao(*args, **kwargs)
	finally:
		if original is None:
			del sim.print
		else:
			sim.print = original


class TestComponentes(unittest.TestCase):
	def bateria(self, soc=50.0):
		return {"capacidade_kwh": 100, "soc": soc, "soc_minimo": 20.0, "soc_maximo": 95.0,
			"p_max_carga": 50, "p_max_descarga": 50, "eficiencia": 0.95}

	def test_bateria_nunca_desce_do_soc_minimo(self):
		bateria = self.bateria(25.0)
		entregue = sim.componente_bateria_descarregar(bateria, 50)
		self.assertAlmostEqual(entregue, 5.0)
		self.assertAlmostEqual(bateria["soc"], 20.0)

	def test_bateria_respeita_reserva(self):
		bateria = self.bateria(60.0)
		entregue = sim.componente_bateria_descarregar(bateria, 50, reserva_kwh=30)
		self.assertAlmostEqual(entregue, 10.0)   # 40 kWh úteis - 30 kWh de reserva
		self.assertEqual(sim.componente_bateria_potencia_disponivel(bateria, reserva_kwh=30), 0.0)

	def test_bateria_nao_passa_do_soc_maximo(self):
		bateria = self.bateria(94.0)
		sim.componente_bateria_carregar(bateria, 50)
		self.assertLessEqual(bateria["soc"], 95.0 + 1e-9)

	def test_geracao_fv_zero_a_noite(self):
		self.assertEqual(sim.componente_fv_ler_geracao(22 * 60, 60, 0.1), 0.0)
		self.assertEqual(sim.previsao_fv_ceu_claro(3 * 60, 60), 0.0)
		self.assertAlmostEqual(sim.previsao_fv_ceu_claro(12 * 60, 60), 60.0)

	def test_preco_com_faixa_variavel(self):
		preco, mult = sim.calcular_preco_kwh(19 * 60, 2.0, [[18 * 60, 21 * 60, 1.25]])
		self.assertEqual((preco, mult), (2.5, 1.25))
		self.assertEqual(sim.calcular_preco_kwh(10 * 60, 2.0, [[18 * 60, 21 * 60, 1.25]])[0], 2.0)


class TestEMS(unittest.TestCase):
	def test_rateio_respeita_obc_e_limite(self):
		config = config_demo()
		config["modo_de_carregamento"] = '3-Solar e Bateria'
		sessoes = [{"id": 1, "chegada_minutos": 0, "obc": 7.4, "status": "carregando"},
			{"id": 2, "chegada_minutos": 5, "obc": 22, "status": "carregando"}]
		setpoints = silencioso(sim.ems_ratear_potencia, sessoes, 30, config, 600)
		self.assertEqual(setpoints[1], 7.4)
		self.assertEqual(setpoints[2], 22)

	def test_modo_inteligente_garante_piso_a_todos(self):
		config = config_demo()
		sessoes = [{"id": 1, "chegada_minutos": 0, "obc": 22, "status": "carregando"},
			{"id": 2, "chegada_minutos": 5, "obc": 3.7, "status": "carregando"}]
		# 26 kW disponíveis: sem o piso, o 1º EV levaria 22 e o 2º ficaria parado
		setpoints = silencioso(sim.ems_ratear_potencia, sessoes, 26, config, 600)
		self.assertGreater(setpoints[2], 0)
		self.assertLessEqual(sum(setpoints.values()), 26 + 1e-9)

	def test_reserva_zera_na_ponta_e_e_positiva_antes(self):
		config = config_demo()
		estado = sim.ems_novo_estado()
		self.assertEqual(sim.ems_planejar_reserva(estado, config, config["bateria"], 18 * 60 + 30), 0.0)
		self.assertGreater(sim.ems_planejar_reserva(estado, config, config["bateria"], 16 * 60), 0.0)

	def test_sem_bateria_sem_reserva(self):
		config = config_demo()
		config["bateria"]["capacidade_kwh"] = 0
		self.assertEqual(sim.ems_planejar_reserva(sim.ems_novo_estado(), config, config["bateria"], 600), 0.0)

	def test_aprendizado_de_nebulosidade(self):
		config = config_demo()
		estado = sim.ems_novo_estado()
		ceu_claro = sim.previsao_fv_ceu_claro(12 * 60, config["potencia_pico_kwp"])
		for _ in range(40):   # céu medindo 50% do céu claro
			sim.ems_aprender(estado, config, ceu_claro * 0.5, 12 * 60, {})
		self.assertAlmostEqual(estado["fator_nuvem"], 0.5, places=2)


class TestSimulacao(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.config = config_demo()
		cls.resultados = {r["modo"]: r for r in silencioso(sim.comparar_modos, cls.config, 12345)}

	def test_balanco_de_energia_fecha(self):
		for r in self.resultados.values():
			soma = r["energia_solar_kwh"] + r["energia_bateria_kwh"] + r["energia_rede_kwh"]
			self.assertAlmostEqual(soma, r["energia_entregue_kwh"], delta=0.05)

	def test_simulacao_reproduzivel(self):
		de_novo = silencioso(sim.simular_modo, self.config, '4-Inteligente', 12345)
		self.assertEqual(de_novo["margem_liquida"], self.resultados['4-Inteligente']["margem_liquida"])

	def test_comparativo_nao_altera_config_original(self):
		self.assertEqual(self.config["bateria"]["soc"], self.config["bateria"]["soc_inicial"])

	def test_modo_inteligente_sem_evs_parados(self):
		self.assertEqual(self.resultados['4-Inteligente']["minutos_pausados"], 0)

	def test_modo_inteligente_compra_menos_na_ponta_em_media(self):
		benchmark = silencioso(sim.benchmark_dias, self.config, 10, 7)
		medias = {m["modo"]: m for m in benchmark["medias"]}
		self.assertLess(medias['4-Inteligente']["energia_rede_ponta_kwh"],
			medias['3-Solar e Bateria']["energia_rede_ponta_kwh"])

	def test_cenario_so_rede_usa_apenas_rede(self):
		config = copy.deepcopy(self.config)
		random.seed(1)
		config["cenario"] = '1'
		config = sim.completar_configuracao(config)
		config["modo_de_carregamento"] = '1-Rápido'
		r = silencioso(sim.simular_modo, config, '1-Rápido', 99)
		self.assertEqual(r["energia_solar_kwh"] + r["energia_bateria_kwh"], 0)


class TestSaidas(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		config = config_demo()
		inicial = copy.deepcopy(config)
		random.seed(4242)
		sessoes, totais, nao = silencioso(sim.executar_simulacao, config, False)
		indicadores = sim.calcular_indicadores(config, sessoes, totais, nao)
		telemetria, eventos = list(sim.telemetria), list(sim.eventos)
		comparativo = silencioso(sim.comparar_modos, inicial, 4242)
		sim.telemetria[:] = telemetria
		sim.eventos[:] = eventos
		cls.resumo = sim.montar_resumo(config, sessoes, indicadores, comparativo)

	def test_weely_entende_perguntas(self):
		casos = {"quanto co2 eu evitei?": "CO₂", "qual foi a margem de hoje": "margem líquida",
			"como está a bateria?": "banco", "qual o melhor horário pra carregar": "melhor horário",
			"o que você recomenda?": "recomendações", "compare os modos": "modo"}
		for pergunta, esperado in casos.items():
			self.assertIn(esperado, weely.responder(self.resumo, pergunta), pergunta)

	def test_weely_pergunta_desconhecida(self):
		self.assertIn("Não entendi", weely.responder(self.resumo, "xyz abc"))

	def test_weely_conversa_ate_sair(self):
		respostas = iter(["resumo", "sair"])
		weely.conversar(self.resumo, entrada=lambda _: next(respostas))

	def test_dashboard_e_svgs(self):
		import tempfile
		with tempfile.TemporaryDirectory() as pasta:
			caminho = dashboard.gerar_dashboard(self.resumo, os.path.join(pasta, "d.html"))
			with open(caminho, encoding="utf-8") as arquivo:
				conteudo = arquivo.read()
			self.assertIn("<svg", conteudo)
			self.assertIn("Weely", conteudo)
			svgs = dashboard.exportar_svgs(self.resumo, pasta)
			self.assertGreaterEqual(len(svgs), 3)

	def test_escala_bonita(self):
		self.assertEqual(dashboard.escala_bonita(47), (50, 10))
		self.assertEqual(dashboard.numero_br(1234.5), "1.234,5")


if __name__ == "__main__":
	unittest.main()
