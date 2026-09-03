# =============================================================================
# ChargeGrid Intelligence — Simulador Integrado de Eletroposto GoodWe
# SPRINT 3 — Prototipagem Funcional e Integração
# =============================================================================
# ÍNDICE
# 0.  Pré-configuração: bibliotecas, parâmetros globais e funções de apoio
# 1.  CAMADA DE COMPONENTES (drivers simulados / integração de hardware)
#     1.1 Arranjo fotovoltaico (string FV)
#     1.2 Medidor inteligente (smart meter do quadro geral)
#     1.3 Banco de baterias (BMS)
#     1.4 Inversor híbrido GoodWe (ET/ES)
#     1.5 Carregador GoodWe Linha HCA-G2 (wallbox)
#     1.6 Barramento de telemetria e log de eventos
# 2.  CONFIGURAÇÃO INICIAL DO ESTABELECIMENTO
#     2.1 Cenário de energia   2.2 Modo de carregamento   2.3 Modelo do carregador
#     2.4 Usina FV, bateria e inversor   2.5 Pontos de recarga
# 3.  PRECIFICAÇÃO
#     3.1 Preço base   3.2 Horário de funcionamento   3.3 Faixas variáveis
#     3.4 Tarifa de compra da concessionária   3.5 Cálculo do preço aplicado
# 4.  CONTROLADOR EMS (automação / lógica de integração)
#     4.1 Leitura dos sensores   4.2 Despacho de potência   4.3 Rateio entre pontos
# 5.  MOTOR DE SIMULAÇÃO (passo a passo, 5 em 5 minutos)
#     5.1 Geração da demanda de EVs   5.2 Laço temporal   5.3 Sessões de recarga
# 6.  RELATÓRIOS E DASHBOARD
#     6.1 Operacional   6.2 Energético   6.3 Financeiro
#     6.4 Sustentabilidade   6.5 Automação   6.6 Curva diária (gráfico ASCII)
# 7.  EXPORTAÇÃO DE DADOS (CSV / JSON / LOG)
# 8.  EXECUÇÃO (main)
# =============================================================================

# 0. PRÉ-CONFIGURAÇÃO
import argparse
import csv
import json
import math
import os
import random
import time
from datetime import datetime

# --- Parâmetros físicos e de referência ------------------------------------
PASSO_MINUTOS = 5                 # resolução temporal da simulação (telemetria)
NASCER_DO_SOL = 6.0               # hora aproximada do início da geração FV
POR_DO_SOL = 18.0                 # hora aproximada do fim da geração FV
FATOR_EMISSAO_REDE = 0.0817       # kgCO2/kWh — média do SIN (referência MCTI)
FATOR_EMISSAO_COMBUSTAO = 1.155   # kgCO2/kWh equivalente de um carro a gasolina
ESPERA_MAXIMA_MINUTOS = 30        # tempo máximo que um EV espera antes da retaguarda da rede
TARIFA_REDE_FORA_PONTA = 0.85     # R$/kWh pagos à concessionária
TARIFA_REDE_PONTA = 1.45          # R$/kWh no horário de ponta (18h-21h)
HORA_PONTA_INICIO = 18
HORA_PONTA_FIM = 21
CREDITO_INJECAO = 0.55            # R$/kWh de crédito por excedente injetado na rede
COMISSAO_ESTABELECIMENTO = 0.10   # 10% da receita bruta

# perfil típico de consumo do prédio (fator por hora do dia)
PERFIL_CONSUMO_PREDIAL = {
	0: 0.25, 1: 0.22, 2: 0.20, 3: 0.20, 4: 0.22, 5: 0.30,
	6: 0.45, 7: 0.65, 8: 0.85, 9: 1.00, 10: 1.05, 11: 1.10,
	12: 1.15, 13: 1.10, 14: 1.05, 15: 1.00, 16: 0.95, 17: 0.90,
	18: 0.85, 19: 0.75, 20: 0.60, 21: 0.45, 22: 0.35, 23: 0.28
}

MODELOS_CARROS_BATERIAS = {
	"Urbano":          (30, 45),
	"Intermediário":   (45, 65),
	"Longa Distância": (70, 90),
	"Premium":         (100, 120)
}
OBC_POSSIVEIS = [3.7, 7.4, 11, 22]   # potência aceita pelo carregador de bordo do EV

VELOCIDADE = 1.0                  # multiplicador das pausas (0 = sem pausa)


def pausa(segundos):
	# centraliza os time.sleep para que o modo demonstração possa acelerar tudo
	if VELOCIDADE > 0:
		time.sleep(segundos * VELOCIDADE)


def opcao_invalida(valor=None):
	if valor is None:
		print("Opção inválida.")
	else:
		print(f"Opção '{valor}' inválida.")


def formatar_horario(horario_em_minutos):
	hh = int(horario_em_minutos) // 60 % 24
	mm = int(horario_em_minutos) % 60
	return f"{hh:02d}:{mm:02d}"


def formatar_faixa_horaria(horario_inicio, horario_fim):
	return f"{horario_inicio}-{horario_fim}"


def barra(valor, maximo, largura=28, caractere="#"):
	if maximo <= 0:
		return ""
	return caractere * int(round(largura * valor / maximo))


def titulo(texto, largura=118, caractere="="):
	print()
	print(caractere * largura)
	print(texto.center(largura))
	print(caractere * largura)


# =============================================================================
# 1. CAMADA DE COMPONENTES (cada função abaixo representa um equipamento real
#    do protótipo; em campo, elas seriam substituídas pela leitura Modbus/API
#    do inversor GoodWe, do medidor e do carregador HCA-G2)
# =============================================================================

# 1.1 Arranjo fotovoltaico — curva de geração ao longo do dia
def componente_fv_ler_geracao(minuto_do_dia, potencia_pico_kwp, nebulosidade):
	hora = (minuto_do_dia % 1440) / 60
	if hora <= NASCER_DO_SOL or hora >= POR_DO_SOL:
		return 0.0
	fator_solar = math.sin(math.pi * (hora - NASCER_DO_SOL) / (POR_DO_SOL - NASCER_DO_SOL))
	ruido = random.uniform(0.90, 1.05)   # nuvens passageiras / sujidade
	geracao = potencia_pico_kwp * fator_solar * (1 - nebulosidade) * ruido
	return max(0.0, round(geracao, 2))


# 1.2 Medidor inteligente — consumo das cargas internas do estabelecimento
def componente_medidor_ler_consumo(minuto_do_dia, consumo_base_kw):
	hora = int((minuto_do_dia % 1440) / 60)
	fator = PERFIL_CONSUMO_PREDIAL[hora]
	return round(consumo_base_kw * fator * random.uniform(0.92, 1.08), 2)


# 1.3 Banco de baterias — BMS simplificado (carga, descarga e proteção de SoC)
def componente_bateria_carregar(bateria, energia_kwh):
	if bateria["capacidade_kwh"] <= 0 or energia_kwh <= 0:
		return 0.0
	espaco = bateria["capacidade_kwh"] * (bateria["soc_maximo"] - bateria["soc"]) / 100
	energia_aceita = min(energia_kwh * bateria["eficiencia"], espaco)
	bateria["soc"] += (energia_aceita / bateria["capacidade_kwh"]) * 100
	return energia_aceita / bateria["eficiencia"]   # energia retirada do barramento


def componente_bateria_descarregar(bateria, energia_kwh):
	if bateria["capacidade_kwh"] <= 0 or energia_kwh <= 0:
		return 0.0
	disponivel = bateria["capacidade_kwh"] * (bateria["soc"] - bateria["soc_minimo"]) / 100
	energia_entregue = min(energia_kwh, max(0.0, disponivel))
	bateria["soc"] -= (energia_entregue / bateria["capacidade_kwh"]) * 100
	return energia_entregue


def componente_bateria_potencia_disponivel(bateria):
	# potência que o BMS libera agora, respeitando SoC mínimo e limite de descarga
	if bateria["capacidade_kwh"] <= 0 or bateria["soc"] <= bateria["soc_minimo"]:
		return 0.0
	energia_util = bateria["capacidade_kwh"] * (bateria["soc"] - bateria["soc_minimo"]) / 100
	potencia_por_energia = energia_util * (60 / PASSO_MINUTOS)
	return round(min(bateria["p_max_descarga"], potencia_por_energia), 2)


# 1.4 Inversor híbrido — limita a potência total que trafega pelo barramento CA
def componente_inversor_limitar(potencia_kw, capacidade_inversor):
	if capacidade_inversor <= 0:
		return potencia_kw
	return min(potencia_kw, capacidade_inversor)


# 1.5 Carregador HCA-G2 — traduz o modelo adquirido em limites elétricos
def componente_carregador_especificacao(potencia_kw):
	if potencia_kw == 7:
		return {"modelo": "GW7K-HCA-20", "tipo_rede": "monofásico", "potencia": 7, "potencia_minima": 1.4}
	elif potencia_kw == 11:
		return {"modelo": "GW11K-HCA-20", "tipo_rede": "trifásico", "potencia": 11, "potencia_minima": 4.2}
	else:
		return {"modelo": "GW22K-HCA-20", "tipo_rede": "trifásico", "potencia": 22, "potencia_minima": 4.2}


# 1.6 Barramento de telemetria e log de eventos (o que o dashboard/IA consome)
telemetria = []      # uma linha a cada PASSO_MINUTOS
eventos = []         # comandos automatizados emitidos pelo EMS


def registrar_evento(minuto, origem, mensagem, categoria="INFO"):
	eventos.append({
		"horario": formatar_horario(minuto),
		"origem": origem,
		"categoria": categoria,
		"mensagem": mensagem
	})


# =============================================================================
# 2. CONFIGURAÇÃO INICIAL DO ESTABELECIMENTO
# =============================================================================

def dimensionar_usina(cenario):
	# 2.4 Usina FV, bateria e inversor (dados que viriam do cadastro da unidade)
	if cenario == '2':
		capacidade_inversor = random.choice([30, 50, 75, 100])
		potencia_pico_kwp = round(capacidade_inversor * random.uniform(1.1, 1.35), 1)
		capacidade_bateria = random.choice([60, 80, 100, 112])
	else:
		capacidade_inversor = 0
		potencia_pico_kwp = 0.0
		capacidade_bateria = 0

	bateria = {
		"capacidade_kwh": capacidade_bateria,
		"soc": 55.0 if capacidade_bateria else 0.0,
		"soc_inicial": 55.0 if capacidade_bateria else 0.0,
		"soc_minimo": 20.0,
		"soc_maximo": 95.0,
		"p_max_carga": round(capacidade_bateria * 0.5, 1),
		"p_max_descarga": round(capacidade_bateria * 0.5, 1),
		"eficiencia": 0.95
	}
	return capacidade_inversor, potencia_pico_kwp, bateria


def minutos_horario(inicial_final):
	while True:
		if inicial_final == 'inicial':
			horario = input("Digite o horário inicial (hh:mm): ")
		else:
			horario = input("Digite o horário final (hh:mm): ")
		try:
			partes_horario = horario.split(":")
			horas = int(partes_horario[0])
			minutos = int(partes_horario[1])
			if 0 <= horas <= 23 and 0 <= minutos <= 59:
				return horas * 60 + minutos
			opcao_invalida(horario)
		except (ValueError, IndexError):
			opcao_invalida(horario)
			print("Digite o horário no formato indicado (ex: 08:30)")


def horario_dentro_funcionamento(horario_min, abertura_min, fechamento_min):
	# se funcionamento é 24h, qualquer horário é validado:
	if abertura_min == fechamento_min:
		return True
	# caso normal (ex: 8h-22h)
	if abertura_min < fechamento_min:
		return abertura_min <= horario_min < fechamento_min
	# caso virando meia-noite (ex: 20h-6h)
	return horario_min >= abertura_min or horario_min < fechamento_min


def minutos_restantes_funcionamento(ponteiro, abertura, fechamento):
	if abertura == fechamento:
		return 1440
	if abertura < fechamento:
		return fechamento - ponteiro
	if ponteiro >= abertura:
		return (1440 - ponteiro) + fechamento
	return fechamento - ponteiro


def configurar_interativo():
	config = {}
	print()
	print("Boas-vindas! Vamos configurar seu eletroposto GoodWe.")
	print()

	# 2.1 Cenário de energia do estabelecimento
	print("""Selecione o sistema de energia do estabelecimento:
1. Apenas rede elétrica.
2. Rede elétrica e energia fotovoltaica.""")
	while True:
		opcao = input("Escolha (1 ou 2): ")
		if opcao in ['1', '2']:
			config["cenario"] = opcao
			break
		opcao_invalida(opcao)

	# 2.2 Modo de carregamento padrão
	print()
	if config["cenario"] == '1':
		pausa(1)
		print("Sistema de rede elétrica.")
		pausa(1)
		print("O modo de carregamento será nominal proveniente da fonte.")
		config["modo_de_carregamento"] = '1-Rápido'
	else:
		print("Sistema de rede elétrica e fotovoltaica.")
		print()
		pausa(1.5)
		print("Selecione a configuração do modo de carregamento para seu estabelecimento:")
		pausa(1)
		print("1. RÁPIDO: giro alto de carros. Consome de qualquer fonte (solar, bateria e rede) na potência cheia.")
		pausa(1)
		print("2. PRIORIDADE SOLAR: uso diurno e economia. Consome apenas o excedente solar; cargas internas têm prioridade.")
		pausa(1)
		print("3. SOLAR E BATERIA: independência da rede. Consome solar + bateria e só usa a rede como retaguarda.")
		print()
		pausa(1)
		while True:
			entrada_modo = input("Defina o modo de carregamento desejado (1, 2 ou 3): ")
			if entrada_modo == '1':
				config["modo_de_carregamento"] = '1-Rápido'
				break
			elif entrada_modo == '2':
				config["modo_de_carregamento"] = '2-Prioridade Solar'
				break
			elif entrada_modo == '3':
				config["modo_de_carregamento"] = '3-Solar e Bateria'
				break
			opcao_invalida(entrada_modo)

	# 2.3 Modelo de carregador GoodWe
	pausa(1)
	print()
	print("Selecione o modelo de carregador adquirido da Linha HCA-G2:")
	print("  GW7K-HCA-20  → 7 kW   (monofásico, 230V)")
	print("  GW11K-HCA-20 → 11 kW  (trifásico, 400V)")
	print("  GW22K-HCA-20 → 22 kW  (trifásico, 400V)")
	print()
	while True:
		entrada = input("Digite a potência (kW) do carregador adquirido: 7, 11 ou 22: ")
		if entrada in ['7', '11', '22']:
			config["carregador"] = componente_carregador_especificacao(int(entrada))
			print()
			print(f"{config['carregador']['modelo']} ({config['carregador']['tipo_rede']}) configurado.")
			break
		opcao_invalida(entrada)

	# 2.5 Pontos de recarga (permite demonstrar o balanceamento dinâmico)
	print()
	while True:
		entrada = input("Quantos pontos de recarga (conectores) serão instalados? (1 a 4): ")
		if entrada in ['1', '2', '3', '4']:
			config["pontos_de_recarga"] = int(entrada)
			break
		opcao_invalida(entrada)

	# 3.1 Preço base por kWh
	print()
	print("Defina o preço por kWh para o usuário final (média de mercado hoje é R$ 2,00/kWh)")
	while True:
		try:
			preco = float(input("R$: ").replace(',', '.'))
			if 0 < preco <= 10:
				print(f"Preço definido: R$ {preco:.2f}/kWh")
				config["preco_kwh"] = preco
				break
			print("Preço fora da faixa razoável (R$ 0,00-10,00), tente novamente.")
		except ValueError:
			opcao_invalida()

	# 3.2 Horário de funcionamento
	print()
	pausa(1)
	print("Defina o horário de funcionamento do eletroposto.")
	config["abertura"] = minutos_horario('inicial')
	config["fechamento"] = minutos_horario('final')
	if config["abertura"] == config["fechamento"]:
		print("\nEletroposto configurado para funcionamento 24 horas.")

	# 3.3 Faixa de horário com preço diferenciado
	config["horarios_valor_variavel"] = []
	print()
	while True:
		resposta = input("Deseja adicionar uma faixa de horário com preço diferenciado (sim/não)? ").lower()
		if resposta in ["sim", "não", "nao"]:
			break
		print("Digite 'sim' ou 'não'.")
	if resposta == 'sim':
		while True:
			inicio_variavel = minutos_horario('inicial')
			if horario_dentro_funcionamento(inicio_variavel, config["abertura"], config["fechamento"]):
				break
			print("Horário deve estar dentro do funcionamento. Tente novamente.")
		while True:
			fim_variavel = minutos_horario('final')
			if horario_dentro_funcionamento(fim_variavel, config["abertura"], config["fechamento"]):
				break
			print("Horário deve estar dentro do funcionamento. Tente novamente.")
		while True:
			try:
				multiplicador = float(input("Variação do preço (ex: 1.2 para +20%): ").replace(',', '.'))
				if multiplicador > 0:
					break
				opcao_invalida(multiplicador)
			except ValueError:
				opcao_invalida()
		config["horarios_valor_variavel"].append([inicio_variavel, fim_variavel, multiplicador])
		faixa_formatada = formatar_faixa_horaria(formatar_horario(inicio_variavel), formatar_horario(fim_variavel))
		print(f"Faixa de horário com variação adicionada: {faixa_formatada} -> {multiplicador:.0%}")

	return config


def configurar_automatico():
	# Modo demonstração (usado no vídeo técnico): dispensa digitação e mantém
	# exatamente a mesma estrutura de configuração do modo interativo.
	config = {
		"cenario": '2',
		"modo_de_carregamento": '3-Solar e Bateria',
		"carregador": componente_carregador_especificacao(22),
		"pontos_de_recarga": 2,
		"preco_kwh": 2.00,
		"abertura": 7 * 60,
		"fechamento": 22 * 60,
		"horarios_valor_variavel": [[18 * 60, 21 * 60, 1.25]]
	}
	print()
	print("Modo demonstração: carregando perfil padrão do eletroposto ChargeGrid...")
	pausa(1)
	return config


def completar_configuracao(config):
	capacidade_inversor, potencia_pico_kwp, bateria = dimensionar_usina(config["cenario"])
	config["capacidade_inversor"] = capacidade_inversor
	config["potencia_pico_kwp"] = potencia_pico_kwp
	config["bateria"] = bateria
	config["nebulosidade"] = round(random.uniform(0.05, 0.30), 2)
	config["consumo_base_kw"] = round(max(8.0, capacidade_inversor * 0.35 if capacidade_inversor else 18.0), 1)
	config["duracao_funcionamento"] = minutos_restantes_funcionamento(
		config["abertura"], config["abertura"], config["fechamento"])
	config["horario_de_funcionamento"] = formatar_faixa_horaria(
		formatar_horario(config["abertura"]), formatar_horario(config["fechamento"]))
	# potência total instalada em conectores
	config["potencia_instalada_kw"] = config["carregador"]["potencia"] * config["pontos_de_recarga"]
	return config


def relatorio_configuracao(config):
	pausa(1)
	print()
	print("Buscando dados do sistema de energia do estabelecimento...")
	pausa(2)
	print("Coleta de dados concluída.")
	pausa(1)

	titulo("CONFIGURAÇÃO CONCLUÍDA — ARQUITETURA INTEGRADA")
	print(f"Cenário de energia:                          {'Rede + Fotovoltaica' if config['cenario'] == '2' else 'Apenas rede elétrica'}")
	print(f"Usina fotovoltaica:                          {config['potencia_pico_kwp']:.1f} kWp (nebulosidade média {config['nebulosidade']:.0%})")
	print(f"Inversor híbrido:                            {config['capacidade_inversor']} kW")
	print(f"Banco de baterias:                           {config['bateria']['capacidade_kwh']} kWh (SoC inicial {config['bateria']['soc']:.0f}%)")
	print(f"Consumo base do estabelecimento:             {config['consumo_base_kw']:.1f} kW")
	print(f"Modelo do carregador:                        {config['carregador']['modelo']}")
	print(f"Tipo de rede:                                {config['carregador']['tipo_rede']}")
	print(f"Pontos de recarga:                           {config['pontos_de_recarga']} x {config['carregador']['potencia']} kW = {config['potencia_instalada_kw']} kW")
	print(f"Potência mínima de partida:                  {config['carregador']['potencia_minima']} kW")
	print(f"Modo de carregamento padrão:                 {config['modo_de_carregamento']}")
	print(f"Horário de funcionamento:                    {config['horario_de_funcionamento']}")
	print(f"Preço base ao usuário:                       R$ {config['preco_kwh']:.2f}/kWh")
	print(f"Tarifa da concessionária:                    R$ {TARIFA_REDE_FORA_PONTA:.2f}/kWh (ponta {HORA_PONTA_INICIO}h-{HORA_PONTA_FIM}h: R$ {TARIFA_REDE_PONTA:.2f}/kWh)")
	if config["horarios_valor_variavel"]:
		print("Faixas de horário com valor variável:")
		for inicio, fim, mult in config["horarios_valor_variavel"]:
			faixa = formatar_faixa_horaria(formatar_horario(inicio), formatar_horario(fim))
			print(f"   {faixa} -> {mult:.0%}")
	print("=" * 118)


# =============================================================================
# 3. PRECIFICAÇÃO
# =============================================================================

# 3.4 Tarifa de compra da concessionária (custo do estabelecimento)
def tarifa_rede(minuto_do_dia):
	hora = int((minuto_do_dia % 1440) / 60)
	if HORA_PONTA_INICIO <= hora < HORA_PONTA_FIM:
		return TARIFA_REDE_PONTA
	return TARIFA_REDE_FORA_PONTA


# 3.5 Cálculo de preço base + faixa de horário com variável
def calcular_preco_kwh(horario_atual_minutos, preco_base, horarios_valor_variavel):
	multiplicador_aplicado = 1.0
	for inicio, fim, mult in horarios_valor_variavel:
		if inicio <= fim:
			if inicio <= horario_atual_minutos <= fim:
				multiplicador_aplicado = mult
				break
		else:
			if horario_atual_minutos >= inicio or horario_atual_minutos <= fim:
				multiplicador_aplicado = mult
				break
	return preco_base * multiplicador_aplicado, multiplicador_aplicado


# =============================================================================
# 4. CONTROLADOR EMS — o "cérebro" que integra os componentes
#    A cada passo ele lê os sensores, decide de onde vem cada kW e envia o
#    setpoint de potência para os carregadores (comando automatizado).
# =============================================================================

def ems_calcular_disponibilidade(config, geracao_fv, consumo_predial, bateria, minuto):
	"""Retorna quanta potência o EMS libera para os carregadores e o motivo."""
	excedente_solar = max(0.0, geracao_fv - consumo_predial)
	potencia_bateria = componente_bateria_potencia_disponivel(bateria)
	limite_conectores = config["potencia_instalada_kw"]
	modo = config["modo_de_carregamento"]

	if modo == '1-Rápido':
		disponivel = limite_conectores
		motivo = "modo rápido: rede complementa qualquer déficit"
	elif modo == '2-Prioridade Solar':
		disponivel = componente_inversor_limitar(excedente_solar, config["capacidade_inversor"])
		motivo = "modo prioridade solar: apenas excedente fotovoltaico"
	else:  # 3-Solar e Bateria
		disponivel = componente_inversor_limitar(excedente_solar + potencia_bateria, config["capacidade_inversor"])
		motivo = "modo solar+bateria: excedente FV somado à descarga do banco"

	# proteção: nunca ultrapassar a potência instalada em conectores
	disponivel = min(disponivel, limite_conectores)

	return {
		"disponivel": round(disponivel, 2),
		"excedente_solar": round(excedente_solar, 2),
		"potencia_bateria": potencia_bateria,
		"motivo": motivo,
		"tarifa_rede": tarifa_rede(minuto)
	}


def ems_ratear_potencia(sessoes_ativas, potencia_disponivel, config, minuto):
	"""4.3 Balanceamento dinâmico: divide a potência entre os EVs conectados,
	respeitando o OBC de cada veículo e a potência mínima de partida."""
	potencia_minima = config["carregador"]["potencia_minima"]
	limite_por_ponto = config["carregador"]["potencia"]
	restante = potencia_disponivel
	setpoints = {}

	# ordem de atendimento: quem chegou primeiro tem prioridade (FIFO)
	for sessao in sorted(sessoes_ativas, key=lambda s: s["chegada_minutos"]):
		# potência que o EMS ainda pode entregar neste conector
		folga = min(limite_por_ponto, restante)
		# abaixo do mínimo de modulação o carregador não consegue partir
		if folga < potencia_minima:
			setpoints[sessao["id"]] = 0.0
			if sessao["status"] != "aguardando energia":
				sessao["status"] = "aguardando energia"
				registrar_evento(minuto, "EMS",
					f"Sessão #{sessao['id']} pausada: {folga:.1f} kW abaixo do mínimo de modulação ({potencia_minima} kW)",
					"AJUSTE")
			continue
		# o veículo nunca recebe mais do que o próprio carregador de bordo aceita
		potencia_sessao = round(min(folga, sessao["obc"]), 2)
		setpoints[sessao["id"]] = potencia_sessao
		restante -= potencia_sessao
		if sessao["status"] == "aguardando energia":
			sessao["status"] = "carregando"
			registrar_evento(minuto, "EMS",
				f"Sessão #{sessao['id']} retomada com {potencia_sessao:.1f} kW liberados pelo EMS", "AJUSTE")
	return setpoints


def ems_alocar_fontes(config, energia_kwh, excedente_solar_kwh, bateria, minuto):
	"""Decide a origem de cada kWh entregue: solar > bateria > rede.
	Retorna o dicionário de energia por fonte."""
	restante = energia_kwh
	usado_solar = min(restante, excedente_solar_kwh)
	restante -= usado_solar

	usado_bateria = 0.0
	if restante > 0 and config["modo_de_carregamento"] == '3-Solar e Bateria':
		usado_bateria = componente_bateria_descarregar(bateria, restante)
		restante -= usado_bateria
		if usado_bateria > 0 and bateria["soc"] <= bateria["soc_minimo"] + 0.5:
			registrar_evento(minuto, "BMS",
				f"Banco de baterias atingiu o SoC mínimo de proteção ({bateria['soc_minimo']:.0f}%) — descarga bloqueada",
				"PROTEÇÃO")

	usado_rede = max(0.0, energia_kwh - usado_solar - usado_bateria)
	return {"solar": usado_solar, "bateria": usado_bateria, "rede": usado_rede}


# =============================================================================
# 5. MOTOR DE SIMULAÇÃO
# =============================================================================

# 5.1 Geração da demanda de EVs do dia
def gerar_demanda_de_evs(config):
	quantidade = random.randint(6, 14)
	duracao = config["duracao_funcionamento"]
	chegadas = sorted(random.sample(range(0, max(1, duracao - 60)), min(quantidade, max(1, duracao - 60))))
	frota = []
	for indice, offset in enumerate(chegadas):
		modelo_carro = random.choice(list(MODELOS_CARROS_BATERIAS.keys()))
		bateria_minima, bateria_maxima = MODELOS_CARROS_BATERIAS[modelo_carro]
		capacidade_bateria_carro = round(random.uniform(bateria_minima, bateria_maxima), 1)
		soc_veiculo = random.randint(10, 60)
		energia_atual = capacidade_bateria_carro * (soc_veiculo / 100)
		falta_encher = capacidade_bateria_carro - energia_atual
		obc_veiculo = random.choice(OBC_POSSIVEIS)
		tipo_meta = random.choice(['Valor (R$)', 'Tempo (min)', 'Energia (kWh)'])

		if tipo_meta == 'Valor (R$)':
			valor_meta = random.randint(20, 100)
			energia_meta = valor_meta / config["preco_kwh"]
		elif tipo_meta == 'Tempo (min)':
			minutos_meta = random.randint(15, 120)
			energia_meta = min(obc_veiculo, config["carregador"]["potencia"]) * (minutos_meta / 60)
		else:
			energia_meta = random.randint(10, 60)

		energia_meta = min(energia_meta, falta_encher)

		frota.append({
			"id": indice + 1,
			"modelo": modelo_carro,
			"capacidade_bateria": capacidade_bateria_carro,
			"soc_inicial": soc_veiculo,
			"obc": obc_veiculo,
			"tipo_carregamento_meta": tipo_meta,
			"energia_meta": round(energia_meta, 2),
			"metodo_de_pagamento": random.choice(['Débito', 'Crédito', 'Pix']),
			"chegada_offset": offset
		})
	return frota


def abrir_sessao(ev, config, minuto):
	preco_aplicado, multiplicador = calcular_preco_kwh(
		minuto % 1440, config["preco_kwh"], config["horarios_valor_variavel"])
	return {
		"id": ev["id"],
		"modelo": ev["modelo"],
		"capacidade_bateria": ev["capacidade_bateria"],
		"soc_inicial": ev["soc_inicial"],
		"soc_atual": ev["soc_inicial"],
		"obc": ev["obc"],
		"tipo_carregamento_meta": ev["tipo_carregamento_meta"],
		"metodo_de_pagamento": ev["metodo_de_pagamento"],
		"energia_meta": ev["energia_meta"],
		"chegada_minutos": minuto,
		"horario_chegada": formatar_horario(minuto),
		"preco_aplicado": round(preco_aplicado, 2),
		"multiplicador": multiplicador,
		"kwh_entregue": 0.0,
		"kwh_solar": 0.0,
		"kwh_bateria": 0.0,
		"kwh_rede": 0.0,
		"custo_energia": 0.0,
		"tempo_min": 0,               # tempo total conectado
		"tempo_carregando_min": 0,    # tempo efetivo com energia fluindo
		"tempo_espera_min": 0,        # espera na fila antes de ocupar o conector
		"minutos_aguardando": 0,      # espera acumulada por falta de energia disponível
		"retaguarda": False,          # rede liberada pelo EMS por excesso de espera
		"status": "carregando",
		"horario_fim": None
	}


def encerrar_sessao(sessao, minuto, motivo):
	sessao["status"] = motivo
	sessao["horario_fim"] = formatar_horario(minuto)
	sessao["valor_cobrado"] = round(sessao["kwh_entregue"] * sessao["preco_aplicado"], 2)
	sessao["margem"] = round(sessao["valor_cobrado"] - sessao["custo_energia"], 2)
	if sessao["tempo_carregando_min"] > 0:
		sessao["potencia_media"] = round(sessao["kwh_entregue"] / (sessao["tempo_carregando_min"] / 60), 2)
	else:
		sessao["potencia_media"] = 0.0
	if sessao["kwh_entregue"] > 0:
		sessao["percentual_renovavel"] = round(
			100 * (sessao["kwh_solar"] + sessao["kwh_bateria"]) / sessao["kwh_entregue"], 1)
	else:
		sessao["percentual_renovavel"] = 0.0
	registrar_evento(minuto, "CARREGADOR",
		f"Sessão #{sessao['id']} encerrada ({motivo}): {sessao['kwh_entregue']:.2f} kWh | R$ {sessao['valor_cobrado']:.2f}",
		"SESSÃO")


# 5.2 Laço temporal — o coração do protótipo
def executar_simulacao(config, mostrar_telemetria=True):
	frota = gerar_demanda_de_evs(config)
	bateria = config["bateria"]
	passo_horas = PASSO_MINUTOS / 60

	fila = []
	sessoes_ativas = []
	sessoes_concluidas = []
	proximo_ev = 0
	setpoint_anterior = None
	fila_anterior = 0
	sessoes_no_passo_anterior = 0

	totais = {
		"fv_gerado": 0.0, "consumo_predial": 0.0, "recarga": 0.0,
		"solar": 0.0, "bateria": 0.0, "rede": 0.0,
		"bateria_carregada": 0.0, "injetado_rede": 0.0,
		"custo_energia": 0.0, "credito_injecao": 0.0
	}

	if mostrar_telemetria:
		titulo("TELEMETRIA EM TEMPO REAL — BARRAMENTO DE ENERGIA", 118, "-")
		print(f"| {'Hora':^6} | {'FV kW':^7} | {'Predial':^8} | {'Recarga':^8} | {'Rede kW':^8} | {'SoC %':^6} | {'Sessões':^7} | {'Origem':^16} |")
		print("|" + "-" * 8 + "|" + "-" * 9 + "|" + "-" * 10 + "|" + "-" * 10 + "|" + "-" * 10 + "|" + "-" * 8 + "|" + "-" * 9 + "|" + "-" * 18 + "|")

	for offset in range(0, config["duracao_funcionamento"], PASSO_MINUTOS):
		minuto = (config["abertura"] + offset) % 1440

		# 4.1 Leitura dos sensores (componentes 1.1 e 1.2)
		geracao_fv = componente_fv_ler_geracao(minuto, config["potencia_pico_kwp"], config["nebulosidade"])
		consumo_predial = componente_medidor_ler_consumo(minuto, config["consumo_base_kw"])
		totais["fv_gerado"] += geracao_fv * passo_horas
		totais["consumo_predial"] += consumo_predial * passo_horas

		# chegada de veículos
		while proximo_ev < len(frota) and frota[proximo_ev]["chegada_offset"] <= offset:
			ev = frota[proximo_ev]
			fila.append({"ev": ev, "chegou_em": minuto})
			registrar_evento(minuto, "CARREGADOR",
				f"EV #{ev['id']} ({ev['modelo']}, SoC {ev['soc_inicial']}%) conectado — meta por {ev['tipo_carregamento_meta']}",
				"SESSÃO")
			proximo_ev += 1

		# ocupação dos conectores livres
		while fila and len(sessoes_ativas) < config["pontos_de_recarga"]:
			item = fila.pop(0)
			sessao = abrir_sessao(item["ev"], config, minuto)
			sessao["tempo_espera_min"] = minuto - item["chegou_em"]
			sessoes_ativas.append(sessao)
			registrar_evento(minuto, "EMS",
				f"Sessão #{sessao['id']} iniciada a R$ {sessao['preco_aplicado']:.2f}/kWh (multiplicador {sessao['multiplicador']:.2f})",
				"SESSÃO")
		if fila and len(fila) != fila_anterior:
			registrar_evento(minuto, "EMS",
				f"{len(fila)} veículo(s) em fila: todos os {config['pontos_de_recarga']} conectores ocupados", "FILA")
		fila_anterior = len(fila)

		# 4.2 Despacho de potência
		disponibilidade = ems_calcular_disponibilidade(config, geracao_fv, consumo_predial, bateria, minuto)

		# Regra de retaguarda: se um EV espera energia renovável por mais tempo que o
		# limite configurado, o EMS libera a rede para não penalizar o cliente.
		# uma vez acionada, a retaguarda permanece até o fim da sessão, evitando
		# que o carregamento fique oscilando entre ligado e desligado
		for sessao in sessoes_ativas:
			if not sessao["retaguarda"] and sessao["minutos_aguardando"] >= ESPERA_MAXIMA_MINUTOS:
				sessao["retaguarda"] = True
				registrar_evento(minuto, "EMS",
					f"Retaguarda da rede acionada para a sessão #{sessao['id']}: {ESPERA_MAXIMA_MINUTOS} min sem energia "
					f"renovável (tarifa de compra R$ {disponibilidade['tarifa_rede']:.2f}/kWh)", "COMANDO")
		if any(s["retaguarda"] for s in sessoes_ativas):
			disponibilidade["disponivel"] = config["potencia_instalada_kw"]
			disponibilidade["motivo"] = "retaguarda da rede ativa por tempo de espera"

		setpoints = ems_ratear_potencia(sessoes_ativas, disponibilidade["disponivel"], config, minuto)
		setpoint_total = round(sum(setpoints.values()), 2)

		if setpoint_anterior is not None and abs(setpoint_total - setpoint_anterior) >= 1.0:
			registrar_evento(minuto, "EMS",
				f"Setpoint dos carregadores ajustado de {setpoint_anterior:.1f} kW para {setpoint_total:.1f} kW ({disponibilidade['motivo']})",
				"COMANDO")
		setpoint_anterior = setpoint_total

		# entrega de energia no passo
		excedente_disponivel_kwh = disponibilidade["excedente_solar"] * passo_horas
		energia_recarga_passo = 0.0
		origem_passo = {"solar": 0.0, "bateria": 0.0, "rede": 0.0}

		for sessao in list(sessoes_ativas):
			potencia = setpoints.get(sessao["id"], 0.0)
			if potencia <= 0:
				sessao["tempo_min"] += PASSO_MINUTOS
				sessao["minutos_aguardando"] += PASSO_MINUTOS
				continue

			energia_passo = potencia * passo_horas
			falta_meta = sessao["energia_meta"] - sessao["kwh_entregue"]
			energia_passo = min(energia_passo, falta_meta)
			if energia_passo <= 0:
				sessao["tempo_min"] += PASSO_MINUTOS
				continue
			sessao["minutos_aguardando"] = 0

			fontes = ems_alocar_fontes(config, energia_passo, excedente_disponivel_kwh, bateria, minuto)
			excedente_disponivel_kwh -= fontes["solar"]
			custo = fontes["rede"] * disponibilidade["tarifa_rede"]

			sessao["kwh_entregue"] = round(sessao["kwh_entregue"] + energia_passo, 3)
			sessao["kwh_solar"] += fontes["solar"]
			sessao["kwh_bateria"] += fontes["bateria"]
			sessao["kwh_rede"] += fontes["rede"]
			sessao["custo_energia"] += custo
			sessao["tempo_min"] += PASSO_MINUTOS
			sessao["tempo_carregando_min"] += PASSO_MINUTOS
			sessao["soc_atual"] = min(100.0, sessao["soc_inicial"] + 100 * sessao["kwh_entregue"] / sessao["capacidade_bateria"])
			sessao["status"] = "carregando"

			energia_recarga_passo += energia_passo
			for fonte in origem_passo:
				origem_passo[fonte] += fontes[fonte]
			totais["custo_energia"] += custo

			if sessao["kwh_entregue"] >= sessao["energia_meta"] - 0.01 or sessao["soc_atual"] >= 99.9:
				encerrar_sessao(sessao, minuto, "meta atingida")
				sessoes_ativas.remove(sessao)
				sessoes_concluidas.append(sessao)

		for fonte in origem_passo:
			totais[fonte] += origem_passo[fonte]
		totais["recarga"] += energia_recarga_passo

		# excedente solar que sobrou: carrega a bateria e o restante é injetado
		if excedente_disponivel_kwh > 0.01:
			limite_carga_kwh = bateria["p_max_carga"] * passo_horas
			soc_antes = bateria["soc"]
			armazenado = componente_bateria_carregar(bateria, min(excedente_disponivel_kwh, limite_carga_kwh))
			totais["bateria_carregada"] += armazenado
			excedente_disponivel_kwh -= armazenado
			if armazenado > 0 and soc_antes < bateria["soc_maximo"] <= bateria["soc"] + 0.5:
				registrar_evento(minuto, "BMS", f"Banco de baterias carregado até {bateria['soc']:.0f}% (SoC máximo)", "PROTEÇÃO")
			if excedente_disponivel_kwh > 0.01:
				totais["injetado_rede"] += excedente_disponivel_kwh
				totais["credito_injecao"] += excedente_disponivel_kwh * CREDITO_INJECAO

		# 1.6 Registro no barramento de telemetria
		potencia_rede = round(max(0.0, consumo_predial - geracao_fv) + origem_passo["rede"] / passo_horas, 2)
		linha = {
			"horario": formatar_horario(minuto),
			"minuto": minuto,
			"geracao_fv_kw": geracao_fv,
			"consumo_predial_kw": consumo_predial,
			"potencia_recarga_kw": round(energia_recarga_passo / passo_horas, 2),
			"potencia_rede_kw": potencia_rede,
			"soc_bateria": round(bateria["soc"], 1),
			"sessoes_ativas": len(sessoes_ativas),
			"fila": len(fila),
			"setpoint_kw": setpoint_total,
			"tarifa_rede": disponibilidade["tarifa_rede"]
		}
		telemetria.append(linha)

		# o painel imprime a cada 15 min ou sempre que o número de sessões mudar
		mudou_ocupacao = len(sessoes_ativas) != sessoes_no_passo_anterior
		sessoes_no_passo_anterior = len(sessoes_ativas)
		if mostrar_telemetria and (offset % 15 == 0 or mudou_ocupacao):
			if origem_passo["solar"] >= max(origem_passo["bateria"], origem_passo["rede"]) and origem_passo["solar"] > 0:
				origem = "Solar"
			elif origem_passo["bateria"] >= origem_passo["rede"] and origem_passo["bateria"] > 0:
				origem = "Bateria"
			elif origem_passo["rede"] > 0:
				origem = "Rede"
			else:
				origem = "—"
			print(f"| {linha['horario']:^6} | {geracao_fv:^7.1f} | {consumo_predial:^8.1f} | "
				f"{linha['potencia_recarga_kw']:^8.1f} | {potencia_rede:^8.1f} | {bateria['soc']:^6.0f} | "
				f"{len(sessoes_ativas):^7} | {origem:^16} |")
			pausa(0.04)

	# fechamento: sessões que ainda estavam ativas
	minuto_fechamento = config["fechamento"]
	for sessao in sessoes_ativas:
		encerrar_sessao(sessao, minuto_fechamento, "encerrada no fechamento")
		sessoes_concluidas.append(sessao)
	for item in fila:
		registrar_evento(minuto_fechamento, "EMS",
			f"EV #{item['ev']['id']} não atendido: eletroposto encerrou o expediente", "FILA")

	sessoes_concluidas.sort(key=lambda s: s["chegada_minutos"])
	return sessoes_concluidas, totais, len(fila)


# =============================================================================
# 6. RELATÓRIOS E DASHBOARD
# =============================================================================

def relatorio_operacional(sessoes):
	titulo("RELATÓRIO OPERACIONAL — SESSÕES DE RECARGA")
	cabecalho = (f"| {'#':^3} | {'Início':^6} | {'Fim':^6} | {'Modelo EV':^15} | {'Meta':^14} | "
		f"{'SoC':^11} | {'kWh':^7} | {'P.méd':^6} | {'Solar%':^6} | {'Mult':^5} | {'R$':^8} | {'Pgto':^8} |")
	print(cabecalho)
	print("-" * len(cabecalho))
	for s in sessoes:
		soc = f"{s['soc_inicial']:.0f}→{s['soc_atual']:.0f}%"
		print(f"| {s['id']:^3} | {s['horario_chegada']:^6} | {str(s['horario_fim']):^6} | {s['modelo']:^15} | "
			f"{s['tipo_carregamento_meta']:^14} | {soc:^11} | {s['kwh_entregue']:^7.2f} | "
			f"{s['potencia_media']:^6.1f} | {s['percentual_renovavel']:^6.0f} | {s['multiplicador']:^5.2f} | "
			f"{s['valor_cobrado']:^8.2f} | {s['metodo_de_pagamento']:^8} |")
		pausa(0.15)
	print("-" * len(cabecalho))


def relatorio_energetico(config, totais, sessoes):
	titulo("RELATÓRIO ENERGÉTICO — INTEGRAÇÃO DAS FONTES")
	recarga = totais["recarga"] if totais["recarga"] > 0 else 1
	renovavel = totais["solar"] + totais["bateria"]
	print(f"Geração fotovoltaica no dia:            {totais['fv_gerado']:.2f} kWh")
	print(f"Consumo interno do estabelecimento:     {totais['consumo_predial']:.2f} kWh")
	print(f"Energia entregue aos veículos:          {totais['recarga']:.2f} kWh")
	print()
	print("Composição da energia entregue aos EVs:")
	maximo = max(totais["solar"], totais["bateria"], totais["rede"], 0.01)
	print(f"  Solar direta      {totais['solar']:8.2f} kWh ({100*totais['solar']/recarga:5.1f}%) {barra(totais['solar'], maximo)}")
	print(f"  Banco de baterias {totais['bateria']:8.2f} kWh ({100*totais['bateria']/recarga:5.1f}%) {barra(totais['bateria'], maximo)}")
	print(f"  Rede elétrica     {totais['rede']:8.2f} kWh ({100*totais['rede']/recarga:5.1f}%) {barra(totais['rede'], maximo)}")
	print()
	print(f"Índice de renovabilidade da recarga:    {100 * renovavel / recarga:.1f}%")
	print(f"Energia armazenada na bateria:          {totais['bateria_carregada']:.2f} kWh")
	print(f"Excedente injetado na rede:             {totais['injetado_rede']:.2f} kWh")
	print(f"SoC final do banco de baterias:         {config['bateria']['soc']:.1f}% (inicial {config['bateria']['soc_inicial']:.1f}%)")
	if sessoes:
		potencia_media = sum(s["potencia_media"] for s in sessoes) / len(sessoes)
		tempo_conectado = sum(s["tempo_min"] for s in sessoes) / len(sessoes)
		tempo_carregando = sum(s["tempo_carregando_min"] for s in sessoes) / len(sessoes)
		print(f"Potência média por sessão:              {potencia_media:.2f} kW")
		print(f"Tempo médio conectado:                  {tempo_conectado:.0f} min")
		print(f"Tempo médio em carregamento efetivo:    {tempo_carregando:.0f} min")


def relatorio_financeiro(totais, sessoes, nao_atendidos):
	titulo("RELATÓRIO FINANCEIRO")
	receita_bruta = sum(s["valor_cobrado"] for s in sessoes)
	custo = totais["custo_energia"]
	credito = totais["credito_injecao"]
	comissao = receita_bruta * COMISSAO_ESTABELECIMENTO
	economia_solar = (totais["solar"] + totais["bateria"]) * TARIFA_REDE_FORA_PONTA
	print(f"Total de sessões concluídas:            {len(sessoes)} sessões")
	print(f"Veículos não atendidos (fila):          {nao_atendidos}")
	print(f"Energia total faturada:                 {totais['recarga']:.2f} kWh")
	print(f"Receita bruta:                          R$ {receita_bruta:.2f}")
	print(f"Custo de energia comprada da rede:      R$ {custo:.2f}")
	print(f"Crédito por injeção de excedente:       R$ {credito:.2f}")
	print(f"Comissão do estabelecimento (10%):      R$ {comissao:.2f}")
	print(f"Margem operacional líquida:             R$ {receita_bruta - custo - comissao + credito:.2f}")
	if sessoes:
		print(f"Ticket médio por sessão:                R$ {receita_bruta / len(sessoes):.2f}")
	print(f"Economia gerada pelo sistema FV:        R$ {economia_solar:.2f} (energia que deixou de ser comprada)")


def relatorio_sustentabilidade(totais):
	titulo("RELATÓRIO DE SUSTENTABILIDADE")
	renovavel = min(totais["solar"] + totais["bateria"], totais["recarga"])
	co2_evitado_rede = renovavel * FATOR_EMISSAO_REDE
	co2_evitado_combustao = totais["recarga"] * FATOR_EMISSAO_COMBUSTAO
	# 1 árvore adulta absorve cerca de 22 kg de CO2 por ano
	arvores_equivalentes = (co2_evitado_combustao * 365) / 22
	print(f"Energia renovável entregue aos EVs:     {renovavel:.2f} kWh")
	print(f"CO2 evitado vs. energia da rede:        {co2_evitado_rede:.2f} kg (fator SIN {FATOR_EMISSAO_REDE} kgCO2/kWh)")
	print(f"CO2 evitado vs. veículo a combustão:    {co2_evitado_combustao:.2f} kg no dia")
	print(f"Autoconsumo fotovoltaico:               {(100 * min(1.0, (totais['solar'] + totais['bateria_carregada']) / max(totais['fv_gerado'], 0.01))):.1f}% da geração")
	print(f"Projeção anual de CO2 evitado:          {co2_evitado_combustao * 365 / 1000:.2f} toneladas")
	print(f"Equivalente em árvores plantadas:       {arvores_equivalentes:.0f} árvores/ano")


def relatorio_automacao():
	titulo("LOG DE AUTOMAÇÃO — COMANDOS EMITIDOS PELO EMS")
	categorias = {}
	for evento in eventos:
		categorias[evento["categoria"]] = categorias.get(evento["categoria"], 0) + 1
	print(f"Total de eventos automatizados registrados: {len(eventos)}")
	for categoria, quantidade in sorted(categorias.items(), key=lambda item: -item[1]):
		print(f"   {categoria:<12} {quantidade:>4} evento(s)")
	print()
	print("Últimos 12 comandos do controlador:")
	for evento in eventos[-12:]:
		print(f"   [{evento['horario']}] {evento['origem']:<11} {evento['categoria']:<9} {evento['mensagem']}")


def dashboard_curva_diaria():
	titulo("CURVA DIÁRIA — GERAÇÃO x CONSUMO x RECARGA (média por hora)")
	por_hora = {}
	for linha in telemetria:
		hora = int(linha["minuto"] / 60)
		acumulado = por_hora.setdefault(hora, {"fv": [], "predial": [], "recarga": []})
		acumulado["fv"].append(linha["geracao_fv_kw"])
		acumulado["predial"].append(linha["consumo_predial_kw"])
		acumulado["recarga"].append(linha["potencia_recarga_kw"])

	# a mesma escala vale para as três séries, para que possam ser comparadas visualmente
	maximo = 0.01
	for dados in por_hora.values():
		for serie in ("fv", "recarga", "predial"):
			maximo = max(maximo, sum(dados[serie]) / len(dados[serie]))

	print(f"{'Hora':<6}{'FV (S) / Recarga (C) / Predial (p)':<60}")
	# a ordem segue a sequência do expediente (importante em turnos que viram a meia-noite)
	for hora in por_hora:
		dados = por_hora[hora]
		fv = sum(dados["fv"]) / len(dados["fv"])
		predial = sum(dados["predial"]) / len(dados["predial"])
		recarga = sum(dados["recarga"]) / len(dados["recarga"])
		print(f"{hora:02d}h   S{barra(fv, maximo, 40, '█')} {fv:6.1f} kW")
		print(f"      C{barra(recarga, maximo, 40, '▓')} {recarga:6.1f} kW")
		print(f"      p{barra(predial, maximo, 40, '·')} {predial:6.1f} kW")


# =============================================================================
# 7. EXPORTAÇÃO DE DADOS (coleta e disponibilização das informações)
# =============================================================================

def exportar_dados(config, sessoes, totais, pasta="saidas"):
	os.makedirs(pasta, exist_ok=True)
	carimbo = datetime.now().strftime("%Y%m%d_%H%M%S")
	arquivos = []

	caminho_sessoes = os.path.join(pasta, f"sessoes_{carimbo}.csv")
	if sessoes:
		with open(caminho_sessoes, "w", newline="", encoding="utf-8") as arquivo:
			escritor = csv.DictWriter(arquivo, fieldnames=list(sessoes[0].keys()))
			escritor.writeheader()
			escritor.writerows(sessoes)
		arquivos.append(caminho_sessoes)

	caminho_telemetria = os.path.join(pasta, f"telemetria_{carimbo}.csv")
	if telemetria:
		with open(caminho_telemetria, "w", newline="", encoding="utf-8") as arquivo:
			escritor = csv.DictWriter(arquivo, fieldnames=list(telemetria[0].keys()))
			escritor.writeheader()
			escritor.writerows(telemetria)
		arquivos.append(caminho_telemetria)

	caminho_eventos = os.path.join(pasta, f"eventos_{carimbo}.log")
	with open(caminho_eventos, "w", encoding="utf-8") as arquivo:
		for evento in eventos:
			arquivo.write(f"[{evento['horario']}] {evento['origem']} | {evento['categoria']} | {evento['mensagem']}\n")
	arquivos.append(caminho_eventos)

	receita_bruta = sum(s["valor_cobrado"] for s in sessoes)
	resumo = {
		"gerado_em": datetime.now().isoformat(timespec="seconds"),
		"configuracao": {
			"cenario": config["cenario"],
			"modo_de_carregamento": config["modo_de_carregamento"],
			"carregador": config["carregador"],
			"pontos_de_recarga": config["pontos_de_recarga"],
			"potencia_pico_kwp": config["potencia_pico_kwp"],
			"capacidade_inversor_kw": config["capacidade_inversor"],
			"capacidade_bateria_kwh": config["bateria"]["capacidade_kwh"],
			"preco_kwh": config["preco_kwh"],
			"horario_de_funcionamento": config["horario_de_funcionamento"]
		},
		"indicadores": {
			"sessoes": len(sessoes),
			"energia_entregue_kwh": round(totais["recarga"], 2),
			"energia_solar_kwh": round(totais["solar"], 2),
			"energia_bateria_kwh": round(totais["bateria"], 2),
			"energia_rede_kwh": round(totais["rede"], 2),
			"geracao_fv_kwh": round(totais["fv_gerado"], 2),
			"injetado_rede_kwh": round(totais["injetado_rede"], 2),
			"receita_bruta": round(receita_bruta, 2),
			"custo_energia": round(totais["custo_energia"], 2),
			"margem_liquida": round(receita_bruta - totais["custo_energia"]
				- receita_bruta * COMISSAO_ESTABELECIMENTO + totais["credito_injecao"], 2),
			"co2_evitado_kg": round((totais["solar"] + totais["bateria"]) * FATOR_EMISSAO_REDE, 2),
			"eventos_automacao": len(eventos)
		},
		"sessoes": sessoes
	}
	caminho_resumo = os.path.join(pasta, f"resumo_{carimbo}.json")
	with open(caminho_resumo, "w", encoding="utf-8") as arquivo:
		json.dump(resumo, arquivo, ensure_ascii=False, indent=2)
	arquivos.append(caminho_resumo)

	titulo("EXPORTAÇÃO DE DADOS (integração com dashboards e IA Weely)", 118, "-")
	for caminho in arquivos:
		print(f"   Arquivo gerado: {caminho}")
	return arquivos


# =============================================================================
# 8. EXECUÇÃO
# =============================================================================

def main():
	global VELOCIDADE

	analisador = argparse.ArgumentParser(
		description="Simulador integrado de eletroposto GoodWe — ChargeGrid Intelligence (Sprint 3)")
	analisador.add_argument("--auto", action="store_true",
		help="executa com o perfil de demonstração, sem entrada de dados")
	analisador.add_argument("--rapido", action="store_true",
		help="remove as pausas de tela (útil para gravação e testes)")
	analisador.add_argument("--seed", type=int, default=None,
		help="semente aleatória para reproduzir exatamente a mesma simulação")
	analisador.add_argument("--sem-exportar", action="store_true",
		help="não grava os arquivos CSV/JSON/LOG na pasta de saída")
	analisador.add_argument("--saida", default="saidas",
		help="pasta onde os dados coletados serão gravados (padrão: saidas/)")
	argumentos = analisador.parse_args()

	if argumentos.seed is not None:
		random.seed(argumentos.seed)
	if argumentos.rapido or argumentos.auto:
		VELOCIDADE = 0.0

	titulo("ChargeGrid Intelligence — ELETROPOSTO INTELIGENTE GoodWe (protótipo funcional)")
	print("Componentes integrados: arranjo FV → inversor híbrido → banco de baterias → medidor")
	print("inteligente → controlador EMS → carregadores HCA-G2 → telemetria → relatórios.")

	config = configurar_automatico() if argumentos.auto else configurar_interativo()
	config = completar_configuracao(config)
	relatorio_configuracao(config)

	if not argumentos.auto:
		while True:
			iniciar = input("\nDeseja ativar seu eletroposto? Digite 'sim': ").lower()
			if iniciar == 'sim':
				break
			print("Digite 'sim' para ativação.")

	print()
	print("Ativando o eletroposto GoodWe e sincronizando os componentes...")
	pausa(2)
	print("Handshake com inversor, medidor e carregadores concluído.")
	pausa(1)

	sessoes, totais, nao_atendidos = executar_simulacao(config)

	relatorio_operacional(sessoes)
	relatorio_energetico(config, totais, sessoes)
	relatorio_financeiro(totais, sessoes, nao_atendidos)
	relatorio_sustentabilidade(totais)
	relatorio_automacao()
	dashboard_curva_diaria()

	if not argumentos.sem_exportar:
		exportar_dados(config, sessoes, totais, argumentos.saida)

	titulo("DIA ENCERRADO — PROTÓTIPO EXECUTADO COM SUCESSO")


if __name__ == "__main__":
	main()
