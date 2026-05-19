# ÍNDICE
# Pré-configuração: importação de bibliotecas e funções de apoio
# 1. Configuração inicial do estabelecimento
# 1.1 Cenário de energia do estabelecimento
# 1.2 Modo de carregamento padrão
# 1.2.1 Geração e consumo de energia solar do estabelecimento
# 1.2.2 Verificação de excedente solar
# 1.3 Modelo de carregador GoodWe
# 1.4 Capacidade da Bateria e Inversor
# 1.5 Relatório do sistema de energia do estabelecimento
# 1.6 Potência final para o carregamento e fonte de energia proveniente
# 2. Precificação
# 2.1 Preço base por kWh
# 2.2.1 Horários de funcionamento
# 2.2.2 Faixa de horário com variável
# 2.2.2.3 Setup multiplicador variável
# 2.3 Cálculo de preço base + faixa de horário com variável
# 3. Relatório de configuração concluída
# 4. Simulação das sessões de recargas
# 4.1 Preparação do cenário de simulação
# 4.2 Simulação do dia em loop de carros
# 5. Relatório final
# 5.1 Relatório operacional
# 5.2 Relatório financeiro



# PRÉ-CONFIGURAÇÃO
# Importação de bibliotecas
import random  # para simulações fictícias
import time
from datetime import datetime

# Função opção inválida
def opcao_invalida(valor=None):
	if valor is None:
		print("Opção inválida.")
	else:
		print(f"Opção '{valor}' inválida.")


# 1. CONFIGURAÇÃO INICIAL DO ESTABELECIMENTO
print()
print("Boas-vindas! Vamos configurar seu eletroposto GoodWe.")
print()

# 1.1 Cenário de energia do estabelecimento (com ou sem painel solar/bateria)
print("""
Selecione o sistema de energia do estabelecimento:
1. Apenas rede elétrica.
2. Rede elétrica e energia fotovoltaica.""")
cenario = None
while True:
	opcao = input("Escolha (1 ou 2): ")
	if opcao not in ['1', '2']:
		opcao_invalida(opcao)
	else:
		cenario = opcao
		break

# 1.2 Modo de carregamento padrão
print()
modo_de_carregamento = None
match cenario:
	case '1':
		time.sleep(1)
		print("Sistema de rede elétrica.")
		time.sleep(1)
		print("O modo de carregamento será nominal proveniente da fonte.")
		modo_de_carregamento = '1-Rápido'
		geracao_solar_atual = 0
		consumo_energia_atual = 0
	case '2':
		print("Sistema de rede elétrica e fotovoltaica.")
		print()
		time.sleep(1.5)
		print(f"Selecione a configuração do modo de carregamento para seu estabelecimento:")
		time.sleep(1.5)
		print("1. RÁPIDO: Recomendado para giro alto de carros. Consome de qualquer fonte: rede elétrica, solar ou bateria. Carregamento na potência cheia.")
		time.sleep(1.5)
		print("2. PRIORIDADE SOLAR: Recomendado para uso diurno e economia. Consome apenas o excedente solar. Cargas internas têm prioridade no consumo.")
		time.sleep(1.5)
		print("3. SOLAR E BATERIA: Recomendado para independência da rede elétrica. Consome solar + bateria armazenada. Mantém autonomia mesmo com sol fraco.")
		print()
		time.sleep(1.5)
		while True:
			entrada_modo = input("Defina o modo de carregamento desejado (1, 2 ou 3): ")
			if entrada_modo == '1':
				modo_de_carregamento = '1-Rápido'
				break
			elif entrada_modo == '2':
				modo_de_carregamento = '2-Prioridade Solar'
				break
			elif entrada_modo == '3':
				modo_de_carregamento = '3-Solar e Bateria'
				break
			else:
				opcao_invalida(entrada_modo)
# 1.2.1 Geração e consumo de energia solar do estabelecimento
		geracao_solar_atual = random.uniform(50, 300)
		consumo_energia_atual = random.uniform(30, 150)

# 1.2.2 Verificação de excedente solar (apenas cenário 2; no cenário 1 é zero)
if geracao_solar_atual > consumo_energia_atual:
	excedente_solar = geracao_solar_atual - consumo_energia_atual
else:
	excedente_solar = 0

# 1.3 Modelo de carregador GoodWe (define potência E tipo de rede)
time.sleep(1)
print()
print("Selecione o modelo de carregador adquirido da Linha HCA-G2:")
time.sleep(1)
print("  GW7K-HCA-20  → 7 kW   (monofásico, 230V)")
print("  GW11K-HCA-20 → 11 kW  (trifásico, 400V)")
print("  GW22K-HCA-20 → 22 kW  (trifásico, 400V)")
print()
time.sleep(1)
potencia_carregador = None
tipo_rede = None
modelo_carregador = None
potencia_minima_rede = None  # 1.4 kW mono / 4.2 kW tri (referência GoodWe)
while True:
	entrada = input("Digite a potência (kW) do carregador adquirido: 7, 11 ou 22: ")
	if entrada not in ['7', '11', '22']:
		opcao_invalida(entrada)
	else:
		potencia_carregador = int(entrada)
		if potencia_carregador == 7:
			tipo_rede = "monofásico"
			modelo_carregador = "GW7K-HCA-20"
			potencia_minima_rede = 1.4
		elif potencia_carregador == 11:
			tipo_rede = "trifásico"
			modelo_carregador = "GW11K-HCA-20"
			potencia_minima_rede = 4.2
		else:
			tipo_rede = "trifásico"
			modelo_carregador = "GW22K-HCA-20"
			potencia_minima_rede = 4.2
		time.sleep(1)
		print()
		print(f"{modelo_carregador} ({tipo_rede}) configurado.")
		break

# 1.4 Capacidade da Bateria e Inversor
if cenario == '2':  # com energia fotovoltaica
	capacidade_bateria_estabelecimento = random.choice([60, 80, 100, 112])
	capacidade_inversor = random.choice([30, 50, 75, 100])
else: # apenas rede elétrica
	capacidade_bateria_estabelecimento = 0
	capacidade_inversor = 0

time.sleep(2)
print()
print("Buscando dados do sistema de energia do estabelecimento...")
time.sleep(3)
print()
print("Coleta de dados concluída.")
time.sleep(2)
print()
print("Gerando relatório do sistema de energia...")
time.sleep(3)

# 1.5 Relatório do sistema de energia do estabelecimento
print()
print(f"{'-'*10} Sistema de energia do estabelecimento {'-'*10}")
print(f"Geração solar atual:                  {geracao_solar_atual:.1f} kW")
print(f"Consumo atual do estabelecimento:     {consumo_energia_atual:.1f} kW")
print(f"Excedente disponível:                 {excedente_solar:.1f} kW")
print(f"Capacidade da bateria:                {capacidade_bateria_estabelecimento} kWh")
print(f"Capacidade do inversor:               {capacidade_inversor} kW")


# 1.6 Potência final para o carregamento e fonte de energia proveniente
match modo_de_carregamento:
	case '1-Rápido':
		potencia_final = potencia_carregador
		fonte_energia = "Rede Elétrica"
	case '2-Prioridade Solar':
		potencia_final = min(excedente_solar, capacidade_inversor, potencia_carregador)
		fonte_energia = "Solar (excedente)"
	case '3-Solar e Bateria':
		potencia_disponivel = excedente_solar + capacidade_inversor
		potencia_final = min(potencia_disponivel, capacidade_inversor, potencia_carregador)
		fonte_energia = "Solar + Bateria"

# validação de potência mínima de partida
if potencia_final < potencia_minima_rede:
	print()
	print(f"Potência disponível ({potencia_final:.1f} kW) abaixo do mínimo da rede {tipo_rede} ({potencia_minima_rede} kW).")
	time.sleep(1.5)
	print()
	print("Ajustando para modo Rápido (rede elétrica)...")
	time.sleep(2)
	modo_de_carregamento = '1-Rápido'
	potencia_final = potencia_carregador
	fonte_energia = "Rede Elétrica"

print()
print(f"Potência final: {potencia_final:.1f} kW | Fonte: {fonte_energia}")
print()
print('-'*120)
print()

# 2. PRECIFICAÇÃO

comissao_estabelecimento = 0.10  # 10% de comissão para o estabelecimento

# 2.1 Preço base por kWh
print("Defina o preço por kWh para o usuário final (média de mercado hoje é R$ 2,00/kWh)")
preco_kwh = None
while True:
	try:
		preco = input("R$: ").replace(',','.')
		preco = float(preco)
		if preco <= 0 or preco > 10:
			print("Preço fora da faixa razoável (R$ 0,00-10,00), tente novamente.")
		else:
			print(f"Preço definido: R$ {preco:.2f}/kWh")
			preco_kwh = preco
			break
	except:
		opcao_invalida(preco)
# 2.2.1 Horários

# horário em minutos
def minutos_horario(inicial_final):
	while True:
		match inicial_final:
			case 'inicial':
				horario = input("Digite o horário inicial (hh:mm) ")
			case 'final':
				horario = input("Digite o horário final (hh:mm) ")
		try:
			partes_horario = horario.split(":")
			horas = int(partes_horario[0])
			minutos = int(partes_horario[1])
			if 0 <= horas <= 23 and 0 <= minutos <= 59:
				horario_em_minutos = horas*60 + minutos
				return horario_em_minutos
			else:
				opcao_invalida(horario)
		except:
			opcao_invalida(horario)
			print("Digite o horário no formato indicado (ex: 08:30)")

def horario_dentro_funcionamento(horario_min, abertura_min, fechamento_min):
# se funcionamento é 24h, qualquer horário é validado:
	if abertura_min == fechamento_min:
		return True
	# caso normal (ex: 8h-22h)
	if abertura_min < fechamento_min:
		return abertura_min <= horario_min < fechamento_min
	else:
		# caso virando meia-noite (ex:20h-6h)
		return horario_min >= abertura_min or horario_min < fechamento_min
	
def minutos_restantes_funcionamento(ponteiro, abertura, fechamento):
	# caso normal (ex: horário de funcionamento de 08h-22h. Chegada às 15h. Restam 5h de funcionamento)
	if abertura < fechamento:
		return fechamento - ponteiro
	# caso virada (ex: horário de funcionamento de 20h-06h. Chegada às 22h. Restam 8h de funcionamento)
	else:
		if ponteiro >= abertura:
			return (1440 - ponteiro) + fechamento
		else:
			return fechamento - ponteiro


# formatação faixa horária
def formatar_faixa_horaria(horario_inicio,horario_fim):
	return f"{horario_inicio}-{horario_fim}"

# formatação apenas horario		
def formatar_horario(horario_em_minutos):
	hh = int(horario_em_minutos) // 60
	mm = int(horario_em_minutos) % 60
	horario_formatado = f"{hh:02d}:{mm:02d}"
	return horario_formatado

# 2.2.1.2 Setup de horário de funcionamento
print()
time.sleep(2)
print("Defina o horário de funcionamento do eletroposto. ")
# solicitar horário inicial e final de funcionamento
horario_inicial_funcionamento_minutos = minutos_horario('inicial')
horario_final_funcionamento_minutos = minutos_horario('final')
# estabelecer regras referente à minutos
if horario_inicial_funcionamento_minutos == horario_final_funcionamento_minutos:
	duracao_funcionamento = 1440 # 24h em minutos
	print(f"\nEletroposto configurado para funcionamento 24 horas.")
else:
	duracao_funcionamento = minutos_restantes_funcionamento(
        horario_inicial_funcionamento_minutos,
        horario_inicial_funcionamento_minutos,
        horario_final_funcionamento_minutos
    )

print()
horario_de_funcionamento = formatar_faixa_horaria(
	formatar_horario(horario_inicial_funcionamento_minutos),
	formatar_horario(horario_final_funcionamento_minutos)
	)
print(f"Horário de funcionamento do eletroposto programado: {horario_de_funcionamento}")
print()

# 2.2.1.3 Faixa de horário com variável
print()
horarios_valor_variavel = []

# pergunta sim/não com validação
while True:
	resposta = input("Deseja adicionar uma faixa de horário com preço diferenciado (sim/não)? ").lower()
	if resposta in ["sim", "não", "nao"]:
		break
	else:
		print("Digite 'sim' ou 'não'.")
if resposta == 'sim':
# solicitar o horário inicial da faixa com variação de preço
	while True:	
		horario_inicial_variavel_minutos = minutos_horario('inicial')
# validar se horário inicial está dentro do horário de funcionamento
		if not horario_dentro_funcionamento(
			horario_inicial_variavel_minutos, 
			horario_inicial_funcionamento_minutos, 
			horario_final_funcionamento_minutos): 
				print(f"Horário deve estar dentro do funcionamento ({horario_de_funcionamento}). Tente novamente.")
		else:
			break
# solicitar o horário final da faixa com variação de preço
	while True:
		horario_final_variavel_minutos = minutos_horario('final')
		if not horario_dentro_funcionamento(
			horario_final_variavel_minutos,
			horario_inicial_funcionamento_minutos,
			horario_final_funcionamento_minutos):
				print(f"Horário deve estar dentro do funcionamento ({horario_de_funcionamento}). Tente novamente.")
# se horário inicial for igual ao horário final:
		elif horario_inicial_variavel_minutos == horario_final_variavel_minutos:
			print("Horário de funcionamento será 24hrs.")
			break
		else:
			break

# 2.2.2.3 Setup multiplicador variável
	while True:
		try:
			multiplicador_variavel = input("Variação do preço (ex: 1.2 para +20%): ").replace(',','.')
			multiplicador_variavel = float(multiplicador_variavel)
			if multiplicador_variavel > 0:
				break
			else:
				opcao_invalida(multiplicador_variavel)
		except:
			opcao_invalida(multiplicador_variavel)
# adicionar faixa na lista (por enquanto apenas uma faixa variável é possível no momento)
		faixa = [horario_inicial_variavel_minutos, horario_final_variavel_minutos, multiplicador_variavel]
		horarios_valor_variavel.append(faixa)

		print(f"Faixa de horário com variação adicionada: {formatar_faixa_horaria(
			formatar_horario(horario_inicial_variavel_minutos),
			formatar_horario(horario_final_variavel_minutos))} -> {multiplicador_variavel:.0%}")
		print()


qtd_horarios = len(horarios_valor_variavel)

# 2.3 Cálculo de preço base + faixa de horário com variável
def calcular_preco_kwh(horario_atual_minutos, preco_base, horarios_valor_variavel):
	multiplicador_aplicado = 1.0  # padrão se não houver faixa de horário com variável
	for faixa in horarios_valor_variavel:
		inicio, fim, mult = faixa
# faixa horária variável normal (ex:08-16h):
		if inicio <= fim:
			if inicio <= horario_atual_minutos <= fim:
				multiplicador_aplicado = mult
				break
# faixa horária variável de virada (ex:22h às 06h):
		else:
			if horario_atual_minutos >= inicio or horario_atual_minutos <= fim:
				multiplicador_aplicado = mult
				break
	return preco_base * multiplicador_aplicado, multiplicador_aplicado

time.sleep(1)
# 3. RELATÓRIO DE CONFIGURAÇÃO CONCLUÍDA
print()
print("Configurando o sistema de recarga...")
time.sleep(3)
print()
print("=" * 120)
print("           CONFIGURAÇÃO CONCLUÍDA")
print("=" * 120)
print(f"Modelo do carregador:                        {modelo_carregador}")
print(f"Tipo de rede:                                {tipo_rede}")
print(f"Modo de carregamento padrão:                 {modo_de_carregamento}")
print(f"Potência efetiva:                            {potencia_final:.1f} kW")
print(f"Preço base:                                  R$ {preco_kwh:.2f}/kWh")
time.sleep(1)
print()
if qtd_horarios > 0:
	print(f"Faixas de horário com valor variável:")
	for faixa in horarios_valor_variavel:
		inicio, fim, mult = faixa
		time.sleep(1)
		print(f"   {formatar_faixa_horaria(formatar_horario(inicio), formatar_horario(fim))} -> {mult:.0%}")
print("=" * 120)
print()
time.sleep(1)

# 4. SIMULAÇÃO DAS SESSÕES DE RECARGAS

while True:
	iniciar_simulacao = input("Deseja ativar seu eletroposto? Digite 'sim': ").lower()
	if iniciar_simulacao != 'sim':
		print("Digite 'sim' para ativação.")
	else:
		break

# Loading para o usuário
print()
print(f"Preparando o sistema...")
time.sleep(2)
print()
print("Ativando o eletroposto Goodwe...")
time.sleep(2)
print()
print("Ativação concluída.")
time.sleep(2)
print()
print("Dados de sessão de recarga serão atualizados em tempo real no relatório operacional.")
print()

# 4.1 Preparação do cenário de simulação

# quantos EVs acessaram o eletroposto
qtd_carros_simulados = random.randint(3, 10) 
# distribuição das sessões de recargas dentro do horário de funcionamento
duracao_funcionamento = minutos_restantes_funcionamento(
	horario_inicial_funcionamento_minutos,
	horario_inicial_funcionamento_minutos,
	horario_final_funcionamento_minutos
)
intervalo_medio = duracao_funcionamento // qtd_carros_simulados
# offset acumulado começa em 0 (no início do funcionamento)
offset_acumulado = 0

# variáveis do relatório diário
total_kwh_dia = 0
receita_bruta_dia = 0          # com variação aplicada
sessoes_dia = []

modelos_carros_baterias = {
	"Urbano":          (30, 45),
	"Intermediário":   (45, 65),
	"Longa Distância": (70, 90),
	"Premium":         (100, 120)
}

obc_possiveis = [3.7, 7.4, 11, 22]  # potência que o carro aceita (On-Board Charger)

# 4.2 Simulação do dia em loop de carros
for carro_id in range(qtd_carros_simulados):
# simular modelo e capacidade de bateria do EV:
	modelo_carro = random.choice(list(modelos_carros_baterias.keys()))
	bateria_minima, bateria_maxima = modelos_carros_baterias[modelo_carro]
	capacidade_bateria_carro = random.uniform(bateria_minima, bateria_maxima)
# simular SoC - State of Charge inicial do EV:
	soc_veiculo = random.randint(10, 60)
	situacao_atual_energia_carro = capacidade_bateria_carro * (soc_veiculo / 100)
	falta_encher_energia_carro = capacidade_bateria_carro - situacao_atual_energia_carro
# simular OBC - OnBoard Charger do EV
	obc_veiculo = random.choice(obc_possiveis)
# calcular potência efetiva (limitada à capacidade do EV):
	potencia_efetiva = min(potencia_final, obc_veiculo)
# simular método de pagamento
	metodo_de_pagamento = random.choice(['Débito', 'Crédito', 'Pix'])
# simular modo de carregamento escolhido pelo motorista (R$/kWh/min):
	tipo_carregamento_meta = random.choice(['Valor (R$)', 'Tempo (min)', 'Energia (kWh)'])
# calcular meta de energia (em kWh) com base na meta de carregamento escolhida
	match tipo_carregamento_meta:
		case 'Valor (R$)':
			valor_meta = random.randint(20, 100)
			energia_meta = valor_meta / preco_kwh
		case 'Tempo (min)':
			min_meta = random.randint(5, 120)
			energia_meta = potencia_efetiva * (min_meta / 60)
		case 'Energia (kWh)':
			energia_meta = random.randint(5, 60)
# validar carregamento até o limite da capacidade de bateria do carro:
	if energia_meta > falta_encher_energia_carro:
		energia_meta = falta_encher_energia_carro

# Sessão de recarga:
# horário de chegada do EV: sorteia quanto tempo de espera até o próximo carro chegar (ou o primeiro)
	espera_aleatoria = random.randint(5,intervalo_medio*2)
# avançar o offset pelo tempo de espera 
	offset_acumulado += espera_aleatoria
# calcular em horário de relógio
	horario_chegada_minutos = (horario_inicial_funcionamento_minutos + offset_acumulado) % 1440
	horario_chegada = formatar_horario(horario_chegada_minutos)
# tempo de sessão de recarga e energia consumida
	tempo_recarga_minutos = (energia_meta / potencia_efetiva) * 60
	energia_entregue = energia_meta
# tempo restante de funcionamento desde o offset acumulado atual
	tempo_restante = duracao_funcionamento - offset_acumulado
# se EV tiver tempo de recarga que ultrapassa horário de funcionamento:
	if tempo_recarga_minutos > tempo_restante:
		continue
# avançar offset para o próximo EV
	offset_acumulado += tempo_recarga_minutos

# calcular custo da sessão
	preco_aplicado, variavel = calcular_preco_kwh(horario_chegada_minutos, preco_kwh, horarios_valor_variavel)
	valor_cobrado = energia_entregue * preco_aplicado  # com variação aplicada

# dados da sessão completa de recarga:
	sessao = {
		"id": carro_id+1,
		"modelo": modelo_carro,
		"capacidade_bateria": round(capacidade_bateria_carro, 1),
		"horario_chegada": horario_chegada,
		"tipo_carregamento_meta": tipo_carregamento_meta,
		"metodo_de_pagamento": metodo_de_pagamento,
		"tempo_min": tempo_recarga_minutos,
		"kwh_entregue": round(energia_entregue, 2),
		"valor_cobrado": round(valor_cobrado, 2),
		"multiplicador": variavel
}
	sessoes_dia.append(sessao)

# acumular nos totais do dia
	total_kwh_dia += energia_entregue
	receita_bruta_dia += valor_cobrado

# 5. RELATÓRIO FINAL
time.sleep(2)
print()
print("=" * 130)
print("                                                    RELATÓRIO OPERACIONAL")
print("=" * 130)
print()

# Cabeçalho da tabela
print(f"| {'#':^3} | {'Horário':^7} | {'Modelo EV':^15} | {'Meta de carregamento em':^23} | {'Recarga Sessão (kWh)':^20} | {'Variável':^10} | {'Valor Cobrado (R$)':^18} | {'Método de Pagamento':^19} |")
# divisória
print("|" + "-" * 5 + "|" + "-" * 9 + "|" + "-" * 17 + "|" + "-" * 25 + "|" + "-" * 22 + "|" + "-" * 12 + "|" + "-" * 20 + "|" + "-" * 21 + "|")

# Dados da tabela
for sessao in sessoes_dia:
	time.sleep(2)
	print(f"| {sessao['id']:^3} | {sessao['horario_chegada']:^7} | {sessao['modelo']:^15} | {sessao['tipo_carregamento_meta']:^23} | {sessao['kwh_entregue']:^20.2f} | {sessao['multiplicador']:^10.2f} | {sessao['valor_cobrado']:^18.2f} | {sessao['metodo_de_pagamento']:^19} |")

time.sleep(2)
print()
print("Dia encerrado.")
print()
time.sleep(2)
print("Gerando relatório financeiro...")
time.sleep(2)
print()
print()
print("=" * 130)
print("                                                    RELATÓRIO FINANCEIRO")
print("=" * 130)
print()
print(f"Total de sessões de recarga:            {len(sessoes_dia)} sessões")
print(f"Energia total entregue:                 {total_kwh_dia:.2f} kWh")
print(f"Receita bruta:                          R$ {receita_bruta_dia:.2f}")
print(f"Comissão estabelecimento (10%):         R$ {comissao_estabelecimento * receita_bruta_dia:.2f}")
print()
print("=" * 130)