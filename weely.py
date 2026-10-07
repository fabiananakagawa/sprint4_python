# =============================================================================
# Weely — assistente virtual do eletroposto ChargeGrid / GoodWe
# SPRINT 4 — integração com assistente virtual
# -----------------------------------------------------------------------------
# Responde, em linguagem natural, perguntas do dono do estabelecimento sobre o
# dia de operação e gera recomendações automáticas a partir da telemetria.
# Roda 100% offline (biblioteca padrão): o reconhecimento de intenção é feito
# por palavras-chave normalizadas, e cada resposta é calculada sobre os dados
# reais exportados pelo simulador (resumo_*.json).
#
# Uso:  python weely.py saidas/resumo_XXXX.json
#       python weely.py saidas/resumo_XXXX.json --pergunta "quanto co2 evitei?"
# =============================================================================

import argparse
import json
import unicodedata


def normalizar(texto):
	sem_acento = unicodedata.normalize("NFD", texto.lower())
	return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn")


def br(valor, casas=1):
	texto = f"{valor:,.{casas}f}"
	return texto.replace(",", "X").replace(".", ",").replace("X", ".")


# --- Respostas por intenção --------------------------------------------------

def resposta_resumo(resumo):
	i = resumo["indicadores"]
	return (f"Hoje o eletroposto atendeu {i['sessoes']} veículos e entregou {br(i['energia_entregue_kwh'])} kWh, "
		f"{br(i['renovabilidade_pct'])}% de origem renovável. A receita foi de R$ {br(i['receita_bruta'], 2)} "
		f"e a margem líquida, R$ {br(i['margem_liquida'], 2)}. Modo usado: {i['modo']}.")


def resposta_renovavel(resumo):
	i = resumo["indicadores"]
	return (f"{br(i['renovabilidade_pct'])}% da recarga foi renovável: {br(i['energia_solar_kwh'])} kWh vieram "
		f"direto do sol e {br(i['energia_bateria_kwh'])} kWh do banco de baterias. Só {br(i['energia_rede_kwh'])} kWh "
		f"foram comprados da rede. O autoconsumo fotovoltaico foi de {br(i['autoconsumo_fv_pct'])}% da geração.")


def resposta_co2(resumo):
	i = resumo["indicadores"]
	return (f"A energia renovável entregue evitou {br(i['co2_evitado_kg'], 2)} kg de CO₂ em relação à rede elétrica "
		f"(fator médio do SIN). Comparado a carros a combustão rodando a mesma distância, foram "
		f"{br(i['co2_evitado_vs_combustao_kg'], 0)} kg de CO₂ a menos no dia — cerca de "
		f"{br(i['co2_evitado_vs_combustao_kg'] * 365 / 1000, 1)} toneladas por ano nesse ritmo.")


def resposta_financeiro(resumo):
	i = resumo["indicadores"]
	return (f"Receita bruta de R$ {br(i['receita_bruta'], 2)}, custo de energia da rede de R$ {br(i['custo_energia'], 2)} "
		f"(R$ {br(i['custo_por_kwh'], 3)} por kWh entregue), comissão do estabelecimento de R$ {br(i['comissao'], 2)} "
		f"e margem líquida de R$ {br(i['margem_liquida'], 2)}. Ticket médio: R$ {br(i['ticket_medio'], 2)}.")


def resposta_rede(resumo):
	i = resumo["indicadores"]
	cfg = resumo["configuracao"]
	texto = (f"Comprei {br(i['energia_rede_kwh'])} kWh da rede, sendo {br(i['energia_rede_ponta_kwh'])} kWh no horário "
		f"de ponta ({cfg['horario_ponta']}, R$ {br(cfg['tarifa_rede_ponta'], 2)}/kWh contra "
		f"R$ {br(cfg['tarifa_rede_fora_ponta'], 2)}/kWh fora dela). Custo total: R$ {br(i['custo_energia'], 2)}.")
	modos = {r["modo"]: r for r in resumo.get("comparativo_modos", [])}
	if i["modo"] == '4-Inteligente' and '3-Solar e Bateria' in modos:
		base = modos['3-Solar e Bateria']
		texto += (f" Sem a previsão do modo inteligente (modo 3), seriam {br(base['energia_rede_ponta_kwh'])} kWh na ponta "
			f"e R$ {br(base['custo_energia'], 2)} de custo.")
	return texto


def resposta_bateria(resumo):
	i = resumo["indicadores"]
	cfg = resumo["configuracao"]
	if not cfg["capacidade_bateria_kwh"]:
		return "Este estabelecimento não tem banco de baterias configurado."
	previsoes = [e for e in resumo["eventos"] if e["categoria"] == "PREVISÃO"]
	texto = (f"O banco de {cfg['capacidade_bateria_kwh']} kWh entregou {br(i['energia_bateria_kwh'])} kWh aos veículos "
		f"e terminou o dia com {br(i['soc_final_bateria'])}% de carga.")
	if previsoes:
		maior = max(previsoes, key=lambda e: e["horario"])
		texto += (f" O EMS ajustou a reserva para a ponta {len(previsoes)} vezes; a última decisão foi às "
			f"{maior['horario']}: \"{maior['mensagem']}\".")
	return texto


def resposta_operacao(resumo):
	i = resumo["indicadores"]
	sessoes = resumo["sessoes"]
	texto = f"{i['sessoes']} sessões concluídas e {i['nao_atendidos']} veículo(s) não atendido(s) por falta de conector livre."
	if sessoes:
		maior = max(sessoes, key=lambda s: s["kwh_entregue"])
		texto += (f" A maior recarga foi a sessão #{maior['id']} ({maior['modelo']}), com {br(maior['kwh_entregue'], 2)} kWh "
			f"e R$ {br(maior['valor_cobrado'], 2)}.")
	if i["minutos_pausados"]:
		texto += f" Somando todos os carros, eles ficaram {i['minutos_pausados']} min parados esperando energia."
	else:
		texto += " Nenhum carro ficou parado esperando energia."
	return texto


def resposta_horario(resumo):
	# hora com maior sobra de sol (geração − prédio − recarga): melhor hora para atrair clientes
	por_hora = {}
	for linha in resumo["telemetria"]:
		hora = linha["minuto"] // 60
		sobra = linha["geracao_fv_kw"] - linha["consumo_predial_kw"] - linha["potencia_recarga_kw"]
		por_hora.setdefault(hora, []).append(sobra)
	medias = {h: sum(v) / len(v) for h, v in por_hora.items()}
	melhor = max(medias, key=medias.get)
	pior = min(medias, key=medias.get)
	return (f"O melhor horário para recarregar é por volta das {melhor:02d}h, quando sobram em média "
		f"{br(medias[melhor])} kW de energia solar. O horário mais crítico é às {pior:02d}h. "
		f"Uma promoção nas horas de sol desloca a demanda para quando a energia é mais barata e limpa.")


def resposta_modos(resumo):
	resultados = resumo.get("comparativo_modos") or []
	if not resultados:
		return "Não há comparativo de modos neste resumo (o cenário usa apenas a rede elétrica)."
	melhor_margem = max(resultados, key=lambda r: r["margem_liquida"])
	mais_verde = max(resultados, key=lambda r: r["renovabilidade_pct"])
	linhas = [f"{r['modo']}: {br(r['renovabilidade_pct'])}% renovável, R$ {br(r['custo_energia'], 2)} de rede, "
		f"margem R$ {br(r['margem_liquida'], 2)}, {r['minutos_pausados']} min parado" for r in resultados]
	texto = ("No mesmo dia, cada modo teria dado: " + "; ".join(linhas) + ". "
		f"Melhor margem: {melhor_margem['modo']}. Mais renovável: {mais_verde['modo']}.")
	benchmark = resumo.get("benchmark")
	if benchmark:
		texto += (f" Na média de {benchmark['dias']} dias, o modo 4 teve margem ≥ modo 3 em "
			f"{benchmark['dias_modo4_melhor_margem_que_modo3']} dias.")
	return texto


def recomendacoes(resumo):
	"""Regras de negócio que transformam os indicadores em ações concretas."""
	i = resumo["indicadores"]
	cfg = resumo["configuracao"]
	dicas = []
	if i["nao_atendidos"] > 0:
		perdido = i["nao_atendidos"] * i["ticket_medio"]
		dicas.append(f"{i['nao_atendidos']} cliente(s) foram embora sem carregar (≈ R$ {br(perdido, 2)} de receita perdida). "
			f"Avalie instalar mais um conector {cfg['carregador']['modelo']}.")
	if i["modo"] != '4-Inteligente' and cfg["cenario"] == '2':
		dicas.append("Ative o modo 4 (Inteligente): ele guarda bateria para a ponta e garante potência mínima a cada carro.")
	if i["energia_rede_ponta_kwh"] > 5 and i["modo"] == '4-Inteligente':
		dicas.append(f"Ainda foram comprados {br(i['energia_rede_ponta_kwh'])} kWh na ponta. Um banco de baterias maior "
			f"ou um multiplicador de preço maior entre 18h e 21h reduziria esse custo.")
	if i["minutos_pausados"] > 0:
		dicas.append(f"Carros ficaram {i['minutos_pausados']} min parados sem energia: isso gera reclamação de cliente.")
	if i["injetado_rede_kwh"] > 5:
		dicas.append(f"{br(i['injetado_rede_kwh'])} kWh de sol sobraram e foram injetados na rede por crédito baixo. "
			f"Um desconto nas horas de sol atrairia mais recargas com essa energia.")
	if cfg["capacidade_bateria_kwh"] and i["soc_final_bateria"] > 60:
		dicas.append(f"A bateria fechou o dia com {br(i['soc_final_bateria'])}%: há folga para estender o expediente "
			f"ou atender mais carros à noite sem comprar da rede.")
	if not dicas:
		dicas.append("A operação está equilibrada: sem fila, sem compra relevante na ponta e sem carros parados.")
	return dicas


def resposta_recomendacoes(resumo):
	return "Minhas recomendações: " + " ".join(f"({n}) {d}" for n, d in enumerate(recomendacoes(resumo), 1))


AJUDA = ("Posso responder sobre: resumo do dia, energia renovável, CO₂, receita e margem, custo da rede e ponta, "
	"bateria, sessões e fila, melhor horário, comparação entre modos e recomendações. Digite 'sair' para encerrar.")

# (palavras-chave, função de resposta) — a primeira intenção que casar responde
INTENCOES = [
	(("ajuda", "help", "o que voce faz", "comandos"), lambda r: AJUDA),
	(("recomend", "sugest", "dica", "melhorar", "o que fazer", "devo"), resposta_recomendacoes),
	(("modo", "compar", "estrategia"), resposta_modos),
	(("co2", "carbono", "emiss", "poluic", "arvore"), resposta_co2),
	(("bateria", "soc", "reserva", "armazen"), resposta_bateria),
	(("horario", "melhor hora", "que horas", "quando"), resposta_horario),
	(("ponta", "rede", "concessionaria", "tarifa", "conta de luz", "custo"), resposta_rede),
	(("renovav", "solar", "sustent", "limpa", "verde", "sol"), resposta_renovavel),
	(("receita", "lucro", "margem", "fatur", "dinheiro", "ganh", "financ", "ticket"), resposta_financeiro),
	(("sess", "carro", "veicul", "cliente", "fila", "atend"), resposta_operacao),
	(("resumo", "como foi", "dia", "status", "geral"), resposta_resumo),
]


def responder(resumo, pergunta):
	texto = normalizar(pergunta)
	for palavras, funcao in INTENCOES:
		if any(palavra in texto for palavra in palavras):
			return funcao(resumo)
	return "Não entendi a pergunta. " + AJUDA


def insights(resumo):
	"""Leitura automática exibida no dashboard: resumo + principais recomendações."""
	return [resposta_resumo(resumo)] + recomendacoes(resumo)[:3]


def conversar(resumo, entrada=input):
	print()
	print("=" * 118)
	print("Weely — assistente virtual do seu eletroposto GoodWe".center(118))
	print("=" * 118)
	print("Oi! Eu analisei o dia de operação. " + AJUDA)
	while True:
		try:
			pergunta = entrada("\nVocê: ").strip()
		except EOFError:
			break
		if not pergunta:
			continue
		if normalizar(pergunta) in ("sair", "tchau", "fim", "exit", "obrigado", "obrigada"):
			print("Weely: Até amanhã! Os dados do dia ficam salvos para o dashboard.")
			break
		print("Weely: " + responder(resumo, pergunta))


if __name__ == "__main__":
	analisador = argparse.ArgumentParser(description="Weely — assistente virtual do eletroposto")
	analisador.add_argument("resumo", help="arquivo resumo_*.json exportado pelo simulador")
	analisador.add_argument("--pergunta", default=None, help="responde uma única pergunta e sai")
	argumentos = analisador.parse_args()
	with open(argumentos.resumo, encoding="utf-8") as arquivo:
		dados = json.load(arquivo)
	if argumentos.pergunta:
		print(responder(dados, argumentos.pergunta))
	else:
		conversar(dados)
