# =============================================================================
# ChargeGrid Intelligence — Adaptador de campo para inversores GoodWe
# SPRINT 4 — caminho do protótipo simulado para o equipamento real
# -----------------------------------------------------------------------------
# No simulador, cada equipamento é um "driver" (componente_fv_ler_geracao,
# componente_medidor_ler_consumo, SoC do BMS...). Este módulo entrega as MESMAS
# grandezas lidas de um inversor híbrido GoodWe real (famílias ET/EH/BT/BH/ES)
# pela rede local, usando a biblioteca open-source `goodwe` (pip install goodwe),
# que conversa com o inversor via protocolo UDP/Modbus.
#
# Se a biblioteca não estiver instalada ou o inversor não responder, o adaptador
# cai automaticamente para uma leitura simulada — o EMS continua funcionando.
#
# ATENÇÃO: este adaptador NÃO foi testado contra um inversor físico (a equipe
# não tem um equipamento disponível). Os nomes dos sensores seguem a
# documentação da biblioteca `goodwe` e devem ser conferidos em campo.
#
# Uso:  python integracao_goodwe.py --ip 192.168.1.50
#       python integracao_goodwe.py --simulado
# =============================================================================

import argparse
import asyncio
import math
import random
from datetime import datetime

# sensores da biblioteca goodwe -> grandezas usadas pelo EMS ChargeGrid
# (potências em W no inversor, convertidas para kW)
MAPA_SENSORES = {
	"geracao_fv_kw": ("ppv", 0.001),
	"consumo_predial_kw": ("house_consumption", 0.001),
	"soc_bateria": ("battery_soc", 1.0),
	"potencia_bateria_kw": ("pbattery1", 0.001),       # > 0 descarregando, < 0 carregando
	"potencia_rede_kw": ("active_power", 0.001),       # sinal depende do modelo: conferir em campo
}


async def ler_inversor_goodwe(ip):
	"""Lê o inversor GoodWe real e devolve as grandezas no formato do EMS."""
	import goodwe   # dependência opcional: só é necessária em campo
	inversor = await goodwe.connect(ip)
	dados = await inversor.read_runtime_data()
	leitura = {"origem": f"GoodWe {inversor.model_name} ({ip})", "horario": datetime.now().strftime("%H:%M:%S")}
	for grandeza, (sensor, fator) in MAPA_SENSORES.items():
		valor = dados.get(sensor)
		leitura[grandeza] = round(valor * fator, 2) if isinstance(valor, (int, float)) else None
	return leitura


def ler_simulado(potencia_pico_kwp=58.0, consumo_base_kw=17.5):
	"""Mesma interface, com valores coerentes com o horário atual (modo demonstração)."""
	agora = datetime.now()
	hora = agora.hour + agora.minute / 60
	sol = max(0.0, math.sin(math.pi * (hora - 6) / 12)) if 6 < hora < 18 else 0.0
	return {
		"origem": "simulado",
		"horario": agora.strftime("%H:%M:%S"),
		"geracao_fv_kw": round(potencia_pico_kwp * sol * random.uniform(0.85, 1.0), 2),
		"consumo_predial_kw": round(consumo_base_kw * random.uniform(0.6, 1.1), 2),
		"soc_bateria": round(random.uniform(40, 90), 1),
		"potencia_bateria_kw": 0.0,
		"potencia_rede_kw": 0.0,
	}


def ler_medicoes(ip=None):
	"""Ponto único de leitura para o EMS: tenta o inversor real e, se falhar, simula."""
	if ip:
		try:
			return asyncio.run(ler_inversor_goodwe(ip))
		except ImportError:
			print("Biblioteca 'goodwe' não instalada (pip install goodwe). Usando leitura simulada.")
		except Exception as erro:   # inversor fora da rede, timeout, modelo não suportado...
			print(f"Não foi possível ler o inversor em {ip} ({erro}). Usando leitura simulada.")
	return ler_simulado()


def excedente_para_carregadores(leitura):
	"""Primeiro passo do EMS sobre a leitura real: quanto sobra de solar para os EVs."""
	fv = leitura.get("geracao_fv_kw") or 0.0
	predial = leitura.get("consumo_predial_kw") or 0.0
	return round(max(0.0, fv - predial), 2)


if __name__ == "__main__":
	analisador = argparse.ArgumentParser(description="Leitura de inversor híbrido GoodWe para o EMS ChargeGrid")
	analisador.add_argument("--ip", default=None, help="IP do inversor GoodWe na rede local")
	analisador.add_argument("--simulado", action="store_true", help="força a leitura simulada")
	argumentos = analisador.parse_args()
	leitura = ler_medicoes(None if argumentos.simulado else argumentos.ip)
	for chave, valor in leitura.items():
		print(f"{chave:<22} {valor}")
	print(f"{'excedente_solar_kw':<22} {excedente_para_carregadores(leitura)}")
