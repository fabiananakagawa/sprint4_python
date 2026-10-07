# =============================================================================
# ChargeGrid Intelligence — Dashboard web e gráficos SVG
# SPRINT 4 — visualização de dados
# -----------------------------------------------------------------------------
# Gera, apenas com a biblioteca padrão:
#   - um dashboard HTML autocontido (abre direto no navegador, modo claro/escuro,
#     tooltips ao passar o mouse e tabelas de apoio);
#   - os mesmos gráficos em SVG estático para o README do GitHub (docs/img).
# Uso direto:  python dashboard.py saidas/resumo_XXXX.json [--svg docs/img]
# =============================================================================

import argparse
import html
import json
import math
import os

# --- Paleta (papéis fixos: cada entidade tem sempre a mesma cor) ------------
# FV/solar = slot 1, recarga dos EVs = slot 2, bateria = slot 3, rede = slot 4
CORES_CLARO = {
	"superficie": "#fcfcfb", "texto": "#0b0b0b", "texto2": "#52514e", "apagado": "#898781",
	"grade": "#e1e0d9", "eixo": "#c3c2b7", "faixa": "#f0efec", "barra_neutra": "#c3c2b7",
	"solar": "#2a78d6", "recarga": "#eb6834", "bateria": "#1baf7a", "rede": "#eda100"
}
# no HTML as cores vêm de variáveis CSS, para o modo escuro trocar tudo em um lugar só
CORES_CSS = {chave: f"var(--{chave.replace('_', '-')})" for chave in CORES_CLARO}

FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'


def esc(texto):
	return html.escape(str(texto), quote=True)


def numero_br(valor, casas=1):
	# 1234.5 -> 1.234,5
	texto = f"{valor:,.{casas}f}"
	return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def com_unidade(valor, unidade, casas=1):
	# moeda vem antes do número (R$ 12,50); demais unidades depois (12,5 kWh)
	if unidade == "R$":
		return f"R$ {numero_br(valor, casas)}"
	return f"{numero_br(valor, casas)} {unidade}"


def escala_bonita(maximo, divisoes=5):
	"""Topo do eixo e passo das marcas em números redondos (1, 2, 2.5, 5 x 10^n)."""
	if maximo <= 0:
		return 1.0, 0.2
	bruto = maximo / divisoes
	potencia = 10 ** math.floor(math.log10(bruto))
	for fator in (1, 2, 2.5, 5, 10):
		passo = fator * potencia
		if passo >= bruto:
			break
	return passo * math.ceil(maximo / passo), passo


def caminho_barra(x, y, largura, altura, raio=4, horizontal=False):
	"""Barra com a ponta de dados arredondada (4px) e a base reta."""
	if altura <= 0 or largura <= 0:
		return ""
	if horizontal:
		r = min(raio, largura, altura / 2)
		return (f"M{x:.1f},{y:.1f} H{x + largura - r:.1f} Q{x + largura:.1f},{y:.1f} {x + largura:.1f},{y + r:.1f} "
			f"V{y + altura - r:.1f} Q{x + largura:.1f},{y + altura:.1f} {x + largura - r:.1f},{y + altura:.1f} "
			f"H{x:.1f} Z")
	r = min(raio, altura, largura / 2)
	return (f"M{x:.1f},{y + altura:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
		f"H{x + largura - r:.1f} Q{x + largura:.1f},{y:.1f} {x + largura:.1f},{y + r:.1f} "
		f"V{y + altura:.1f} Z")


def abrir_svg(largura, altura, cores, rotulo, estatico):
	fundo = f'<rect width="{largura}" height="{altura}" fill="{cores["superficie"]}"/>' if estatico else ""
	# no dashboard o gráfico acompanha a largura do cartão; no README fica no tamanho nativo
	limite = f";max-width:{largura}px" if estatico else ""
	return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {largura} {altura}" '
		f'width="100%" role="img" aria-label="{esc(rotulo)}" '
		f'style="font-family:{esc(FONTE)};font-size:12px{limite}">{fundo}')


def legenda(itens, x, y, cores):
	"""Legenda sempre presente com 2+ séries: traço colorido + texto em tinta neutra."""
	partes = []
	for nome, cor in itens:
		partes.append(f'<line x1="{x}" y1="{y - 4}" x2="{x + 16}" y2="{y - 4}" stroke="{cor}" '
			f'stroke-width="3" stroke-linecap="round"/>')
		partes.append(f'<text x="{x + 22}" y="{y}" fill="{cores["texto2"]}">{esc(nome)}</text>')
		x += 30 + 7.2 * len(nome)
	return "".join(partes)


# =============================================================================
# Gráfico de linhas (séries no tempo, eixo único)
# =============================================================================

def grafico_linhas(minutos, series, unidade, cores, titulo_acessivel, estatico=False,
		faixa_ponta=None, largura=920, altura=320, y_max=None):
	esq, dir_, topo, base = 56, 24, 40, 36
	area_l = largura - esq - dir_
	area_a = altura - topo - base
	n = len(minutos)
	maximo = y_max or max([max(s["valores"]) for s in series] + [0.01])
	topo_eixo, passo = escala_bonita(maximo)

	def px(i):
		return esq + area_l * i / max(1, n - 1)

	def py(valor):
		return topo + area_a * (1 - valor / topo_eixo)

	partes = [abrir_svg(largura, altura, cores, titulo_acessivel, estatico)]
	partes.append(legenda([(s["nome"], s["cor"]) for s in series], esq, 18, cores) if len(series) > 1 else "")

	# faixa do horário de ponta da concessionária (contexto, não dado)
	if faixa_ponta:
		indices = [i for i, m in enumerate(minutos) if faixa_ponta[0] <= m < faixa_ponta[1]]
		if indices:
			x0, x1 = px(indices[0]), px(min(indices[-1] + 1, n - 1))
			partes.append(f'<rect x="{x0:.1f}" y="{topo}" width="{x1 - x0:.1f}" height="{area_a}" fill="{cores["faixa"]}"/>')
			partes.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{topo + 14}" text-anchor="middle" '
				f'fill="{cores["apagado"]}">Ponta da concessionária</text>')

	# grade horizontal (linhas finas e sólidas) e marcas do eixo Y
	valor = 0.0
	while valor <= topo_eixo + 1e-9:
		y = py(valor)
		partes.append(f'<line x1="{esq}" y1="{y:.1f}" x2="{largura - dir_}" y2="{y:.1f}" '
			f'stroke="{cores["eixo"] if valor == 0 else cores["grade"]}" stroke-width="1"/>')
		partes.append(f'<text x="{esq - 8}" y="{y + 4:.1f}" text-anchor="end" fill="{cores["apagado"]}" '
			f'style="font-variant-numeric:tabular-nums">{numero_br(valor, 0 if passo >= 1 else 1)}</text>')
		valor += passo
	partes.append(f'<text x="{esq - 8}" y="{topo - 12}" text-anchor="end" fill="{cores["apagado"]}">{esc(unidade)}</text>')

	# eixo X: uma marca a cada 2 horas cheias
	for i, minuto in enumerate(minutos):
		if minuto % 120 == 0:
			partes.append(f'<text x="{px(i):.1f}" y="{altura - base + 20}" text-anchor="middle" '
				f'fill="{cores["apagado"]}" style="font-variant-numeric:tabular-nums">{minuto // 60 % 24:02d}h</text>')

	# séries: linha de 2px, juntas arredondadas
	for serie in series:
		pontos = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(serie["valores"]))
		partes.append(f'<polyline points="{pontos}" fill="none" stroke="{serie["cor"]}" stroke-width="2" '
			f'stroke-linejoin="round" stroke-linecap="round"/>')

	# camada de interação: retícula vertical + tooltip com todas as séries
	if not estatico:
		partes.append(f'<line class="mira" x1="0" y1="{topo}" x2="0" y2="{topo + area_a}" '
			f'stroke="{cores["apagado"]}" stroke-width="1" visibility="hidden"/>')
		largura_coluna = area_l / max(1, n - 1)
		for i, minuto in enumerate(minutos):
			linhas = [f"{minuto // 60 % 24:02d}:{minuto % 60:02d}"]
			for serie in series:
				linhas.append(f"{serie['nome']}: {numero_br(serie['valores'][i], 1)} {unidade}")
			partes.append(f'<rect class="alvo" x="{px(i) - largura_coluna / 2:.1f}" y="{topo}" '
				f'width="{largura_coluna:.1f}" height="{area_a}" fill="transparent" '
				f'data-x="{px(i):.1f}" data-tip="{esc("|".join(linhas))}"/>')
	partes.append("</svg>")
	return "".join(partes)


# =============================================================================
# Colunas empilhadas por hora (energia por fonte)
# =============================================================================

def grafico_colunas_empilhadas(rotulos, camadas, unidade, cores, titulo_acessivel, estatico=False,
		largura=920, altura=320):
	esq, dir_, topo, base = 56, 24, 40, 36
	area_l = largura - esq - dir_
	area_a = altura - topo - base
	n = len(rotulos)
	totais = [sum(c["valores"][i] for c in camadas) for i in range(n)]
	topo_eixo, passo = escala_bonita(max(totais + [0.01]))
	faixa = area_l / max(1, n)
	espessura = min(24, faixa * 0.6)

	def py(valor):
		return topo + area_a * (1 - valor / topo_eixo)

	partes = [abrir_svg(largura, altura, cores, titulo_acessivel, estatico)]
	partes.append(legenda([(c["nome"], c["cor"]) for c in camadas], esq, 18, cores))
	valor = 0.0
	while valor <= topo_eixo + 1e-9:
		y = py(valor)
		partes.append(f'<line x1="{esq}" y1="{y:.1f}" x2="{largura - dir_}" y2="{y:.1f}" '
			f'stroke="{cores["eixo"] if valor == 0 else cores["grade"]}" stroke-width="1"/>')
		partes.append(f'<text x="{esq - 8}" y="{y + 4:.1f}" text-anchor="end" fill="{cores["apagado"]}" '
			f'style="font-variant-numeric:tabular-nums">{numero_br(valor, 0 if passo >= 1 else 1)}</text>')
		valor += passo
	partes.append(f'<text x="{esq - 8}" y="{topo - 12}" text-anchor="end" fill="{cores["apagado"]}">{esc(unidade)}</text>')

	for i, rotulo in enumerate(rotulos):
		x = esq + faixa * i + (faixa - espessura) / 2
		partes.append(f'<text x="{x + espessura / 2:.1f}" y="{altura - base + 20}" text-anchor="middle" '
			f'fill="{cores["apagado"]}" style="font-variant-numeric:tabular-nums">{esc(rotulo)}</text>')
		acumulado = 0.0
		visiveis = [c for c in camadas if c["valores"][i] > 0.005]
		for indice, camada in enumerate(visiveis):
			valor = camada["valores"][i]
			y_topo = py(acumulado + valor)
			y_base = py(acumulado)
			# 2px de respiro na cor da superfície entre segmentos empilhados
			altura_seg = (y_base - y_topo) - (2 if indice > 0 else 0)
			ultimo = indice == len(visiveis) - 1
			if ultimo:
				partes.append(f'<path d="{caminho_barra(x, y_topo, espessura, altura_seg)}" fill="{camada["cor"]}"/>')
			elif altura_seg > 0:
				partes.append(f'<rect x="{x:.1f}" y="{y_topo:.1f}" width="{espessura:.1f}" '
					f'height="{altura_seg:.1f}" fill="{camada["cor"]}"/>')
			acumulado += valor
		if not estatico:
			linhas = [rotulo] + [f"{c['nome']}: {numero_br(c['valores'][i], 1)} {unidade}" for c in camadas]
			linhas.append(f"Total: {numero_br(totais[i], 1)} {unidade}")
			partes.append(f'<rect class="alvo" x="{esq + faixa * i:.1f}" y="{topo}" width="{faixa:.1f}" '
				f'height="{area_a}" fill="transparent" data-tip="{esc("|".join(linhas))}"/>')
	partes.append("</svg>")
	return "".join(partes)


# =============================================================================
# Pequenos múltiplos de barras horizontais (comparativo entre modos)
# =============================================================================

def grafico_comparativo(resultados, metricas, cores, titulo_acessivel, estatico=False, destaque='4-Inteligente'):
	colunas = 2
	painel_l, painel_a = 450, 40 + 30 * len(resultados)
	largura = painel_l * colunas + 20
	linhas_paineis = math.ceil(len(metricas) / colunas)
	altura = painel_a * linhas_paineis + 10
	partes = [abrir_svg(largura, altura, cores, titulo_acessivel, estatico)]
	for indice, (chave, nome, unidade, casas) in enumerate(metricas):
		ox = (indice % colunas) * (painel_l + 20)
		oy = (indice // colunas) * painel_a
		partes.append(f'<text x="{ox}" y="{oy + 18}" fill="{cores["texto"]}" font-weight="600">{esc(nome)}</text>')
		maximo = max([r[chave] for r in resultados] + [0.01])
		inicio_barra, area = ox + 150, painel_l - 150 - 70
		for j, resultado in enumerate(resultados):
			y = oy + 32 + 30 * j
			valor = resultado[chave]
			cor = cores["solar"] if resultado["modo"] == destaque else cores["barra_neutra"]
			comprimento = area * valor / maximo
			partes.append(f'<text x="{inicio_barra - 8}" y="{y + 12}" text-anchor="end" '
				f'fill="{cores["texto2"]}">{esc(resultado["modo"])}</text>')
			if comprimento > 0.5:
				partes.append(f'<path d="{caminho_barra(inicio_barra, y, comprimento, 16, horizontal=True)}" fill="{cor}"/>')
			partes.append(f'<text x="{inicio_barra + comprimento + 6:.1f}" y="{y + 12}" fill="{cores["texto"]}" '
				f'style="font-variant-numeric:tabular-nums">{esc(com_unidade(valor, unidade, casas))}</text>')
			if not estatico:
				partes.append(f'<rect class="alvo" x="{ox}" y="{y - 6}" width="{painel_l}" height="28" fill="transparent" '
					f'data-tip="{esc(resultado["modo"] + "|" + nome + ": " + com_unidade(valor, unidade, casas))}"/>')
	partes.append("</svg>")
	return "".join(partes)


# =============================================================================
# Preparação dos dados a partir do resumo JSON
# =============================================================================

METRICAS_COMPARATIVO = [
	("custo_energia", "Custo de energia da rede", "R$", 2),
	("energia_rede_ponta_kwh", "Compra no horário de ponta", "kWh", 1),
	("renovabilidade_pct", "Recarga renovável", "%", 1),
	("minutos_pausados", "Tempo de EVs parados", "min", 0),
	("margem_liquida", "Margem líquida", "R$", 2),
	("energia_entregue_kwh", "Energia entregue", "kWh", 1)
]


def preparar_series(resumo, cores):
	telemetria = resumo["telemetria"]
	minutos = [linha["minuto"] for linha in telemetria]
	capacidade = resumo["configuracao"]["capacidade_bateria_kwh"] or 1
	soc_minimo = 20.0
	potencia = [
		{"nome": "Geração FV", "cor": cores["solar"], "valores": [l["geracao_fv_kw"] for l in telemetria]},
		{"nome": "Recarga dos EVs", "cor": cores["recarga"], "valores": [l["potencia_recarga_kw"] for l in telemetria]},
		{"nome": "Consumo do prédio", "cor": cores["apagado"], "valores": [l["consumo_predial_kw"] for l in telemetria]}
	]
	bateria = [
		{"nome": "SoC da bateria", "cor": cores["bateria"], "valores": [l["soc_bateria"] for l in telemetria]},
		{"nome": "Piso planejado pelo EMS (reserva p/ ponta)", "cor": cores["apagado"],
			"valores": [soc_minimo + 100 * l.get("reserva_bateria_kwh", 0) / capacidade for l in telemetria]}
	]
	# energia por fonte agregada por hora
	por_hora = {}
	for linha in telemetria:
		hora = linha["minuto"] // 60
		acumulado = por_hora.setdefault(hora, [0.0, 0.0, 0.0])
		acumulado[0] += linha.get("recarga_solar_kwh", 0)
		acumulado[1] += linha.get("recarga_bateria_kwh", 0)
		acumulado[2] += linha.get("recarga_rede_kwh", 0)
	horas = list(por_hora.keys())
	fontes = [
		{"nome": "Solar direta", "cor": cores["solar"], "valores": [por_hora[h][0] for h in horas]},
		{"nome": "Bateria", "cor": cores["bateria"], "valores": [por_hora[h][1] for h in horas]},
		{"nome": "Rede", "cor": cores["rede"], "valores": [por_hora[h][2] for h in horas]}
	]
	return minutos, potencia, bateria, [f"{h % 24:02d}h" for h in horas], fontes


def faixa_ponta(resumo):
	inicio, fim = resumo["configuracao"]["horario_ponta"].split("-")
	return int(inicio[:2]) * 60, int(fim[:2]) * 60


def gerar_graficos(resumo, cores, estatico):
	minutos, potencia, bateria, horas, fontes = preparar_series(resumo, cores)
	graficos = {
		"potencia": grafico_linhas(minutos, potencia, "kW", cores,
			"Geração FV, recarga dos EVs e consumo do prédio ao longo do dia", estatico, faixa_ponta(resumo)),
		"bateria": grafico_linhas(minutos, bateria, "%", cores,
			"Estado de carga da bateria e piso planejado pelo EMS", estatico, faixa_ponta(resumo), y_max=100),
		"fontes": grafico_colunas_empilhadas(horas, fontes, "kWh", cores,
			"Energia entregue aos EVs por fonte, hora a hora", estatico)
	}
	benchmark = resumo.get("benchmark")
	if benchmark:
		graficos["benchmark"] = grafico_comparativo(benchmark["medias"], METRICAS_COMPARATIVO, cores,
			f"Média de {benchmark['dias']} dias por modo de carregamento", estatico)
	if resumo.get("comparativo_modos"):
		graficos["comparativo"] = grafico_comparativo(resumo["comparativo_modos"], METRICAS_COMPARATIVO, cores,
			"Comparativo dos modos no mesmo dia", estatico)
	return graficos


def exportar_svgs(resumo, pasta):
	"""Gráficos estáticos (cores fixas do modo claro) para o README do GitHub."""
	os.makedirs(pasta, exist_ok=True)
	caminhos = []
	for nome, svg in gerar_graficos(resumo, CORES_CLARO, estatico=True).items():
		caminho = os.path.join(pasta, f"grafico_{nome}.svg")
		with open(caminho, "w", encoding="utf-8") as arquivo:
			arquivo.write(svg)
		caminhos.append(caminho)
	return caminhos


# =============================================================================
# Página HTML
# =============================================================================

ESTILO = """
.viz-root{color-scheme:light;--superficie:#fcfcfb;--pagina:#f9f9f7;--texto:#0b0b0b;--texto2:#52514e;
--apagado:#898781;--grade:#e1e0d9;--eixo:#c3c2b7;--faixa:#f0efec;--barra-neutra:#c3c2b7;--borda:rgba(11,11,11,.10);
--solar:#2a78d6;--recarga:#eb6834;--bateria:#1baf7a;--rede:#eda100;--bom:#006300}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;
--superficie:#1a1a19;--pagina:#0d0d0d;--texto:#fff;--texto2:#c3c2b7;--apagado:#898781;--grade:#2c2c2a;--eixo:#383835;
--faixa:#262624;--barra-neutra:#52514e;--borda:rgba(255,255,255,.10);--solar:#3987e5;--recarga:#d95926;
--bateria:#199e70;--rede:#c98500;--bom:#0ca30c}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--superficie:#1a1a19;--pagina:#0d0d0d;--texto:#fff;
--texto2:#c3c2b7;--apagado:#898781;--grade:#2c2c2a;--eixo:#383835;--faixa:#262624;--barra-neutra:#52514e;
--borda:rgba(255,255,255,.10);--solar:#3987e5;--recarga:#d95926;--bateria:#199e70;--rede:#c98500;--bom:#0ca30c}
*{box-sizing:border-box}body{margin:0}
.viz-root{background:var(--pagina);color:var(--texto);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
min-height:100vh;padding:28px 32px 60px}
.topo{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;max-width:1240px;margin:0 auto 20px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:16px;margin:0 0 4px}.sub{color:var(--texto2);font-size:13px;margin:0}
button{font:inherit;font-size:13px;color:var(--texto);background:var(--superficie);border:1px solid var(--borda);
border-radius:8px;padding:6px 12px;cursor:pointer}
.grade{display:grid;gap:16px;max-width:1240px;margin:0 auto}
.kpis{display:grid;grid-template-columns:1.4fr repeat(3,1fr);gap:16px}
.cartao{background:var(--superficie);border:1px solid var(--borda);border-radius:12px;padding:18px 20px}
.rotulo{color:var(--texto2);font-size:13px}.valor{font-size:26px;font-weight:600;margin-top:6px}
.heroi .valor{font-size:52px;line-height:1.05}.delta{font-size:13px;color:var(--texto2);margin-top:4px}
.delta b{color:var(--bom);font-weight:600}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{padding:6px 8px;border-bottom:1px solid var(--grade);text-align:right;font-variant-numeric:tabular-nums}
th{color:var(--texto2);font-weight:600}th:first-child,td:first-child{text-align:left}
tr.destaque td{font-weight:600}
details summary{cursor:pointer;color:var(--texto2);font-size:13px;margin-top:10px}
.log{font-family:ui-monospace,Consolas,monospace;font-size:12px;max-height:340px;overflow:auto;color:var(--texto2);
white-space:pre-wrap;margin:8px 0 0}
#dica{position:fixed;pointer-events:none;background:var(--superficie);color:var(--texto);border:1px solid var(--borda);
border-radius:8px;padding:8px 10px;font-size:12px;line-height:1.5;box-shadow:0 4px 16px rgba(0,0,0,.12);display:none;
font-variant-numeric:tabular-nums;z-index:10}
.weely{border-left:3px solid var(--solar)}.weely p{margin:6px 0;font-size:14px;color:var(--texto)}
@media (max-width:900px){.kpis{grid-template-columns:1fr}}
"""

SCRIPT = """
const dica=document.getElementById('dica');
document.querySelectorAll('.alvo').forEach(alvo=>{
  const svg=alvo.ownerSVGElement, mira=svg.querySelector('.mira');
  alvo.addEventListener('mousemove',e=>{
    dica.innerHTML=alvo.dataset.tip.split('|').map((l,i)=>i?l:'<b>'+l+'</b>').join('<br>');
    dica.style.display='block';
    dica.style.left=Math.min(e.clientX+14,innerWidth-dica.offsetWidth-8)+'px';
    dica.style.top=(e.clientY+14)+'px';
    if(mira&&alvo.dataset.x){mira.setAttribute('x1',alvo.dataset.x);mira.setAttribute('x2',alvo.dataset.x);
      mira.setAttribute('visibility','visible');}
  });
  alvo.addEventListener('mouseleave',()=>{dica.style.display='none';if(mira)mira.setAttribute('visibility','hidden');});
});
document.getElementById('tema').addEventListener('click',()=>{
  const r=document.documentElement, escuro=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
  r.dataset.theme=escuro?'light':'dark';
});
"""


def cartao_kpi(rotulo, valor, detalhe="", heroi=False):
	classe = "cartao heroi" if heroi else "cartao"
	detalhe_html = f'<div class="delta">{detalhe}</div>' if detalhe else ""
	return f'<div class="{classe}"><div class="rotulo">{esc(rotulo)}</div><div class="valor">{valor}</div>{detalhe_html}</div>'


def tabela(cabecalhos, linhas, destaque=None):
	topo = "".join(f"<th>{esc(c)}</th>" for c in cabecalhos)
	corpo = []
	for linha in linhas:
		classe = ' class="destaque"' if destaque and linha[0] == destaque else ""
		corpo.append(f"<tr{classe}>" + "".join(f"<td>{esc(c)}</td>" for c in linha) + "</tr>")
	return f"<table><thead><tr>{topo}</tr></thead><tbody>{''.join(corpo)}</tbody></table>"


def tabela_modos(resultados):
	cabecalhos = ["Modo", "Renovável %", "Entregue kWh", "Rede kWh", "Ponta kWh", "Custo R$", "Margem R$",
		"Sessões", "Fila", "Parado min", "CO₂ kg"]
	linhas = [[r["modo"], numero_br(r["renovabilidade_pct"]), numero_br(r["energia_entregue_kwh"]),
		numero_br(r["energia_rede_kwh"]), numero_br(r["energia_rede_ponta_kwh"]), numero_br(r["custo_energia"], 2),
		numero_br(r["margem_liquida"], 2), numero_br(r["sessoes"]), numero_br(r["nao_atendidos"]),
		numero_br(r["minutos_pausados"], 0), numero_br(r["co2_evitado_kg"], 2)] for r in resultados]
	return tabela(cabecalhos, linhas, destaque="4-Inteligente")


def gerar_dashboard(resumo, caminho):
	import weely   # os insights em linguagem natural vêm da própria assistente
	graficos = gerar_graficos(resumo, CORES_CSS, estatico=False)
	cfg = resumo["configuracao"]
	ind = resumo["indicadores"]
	insights = weely.insights(resumo)

	comparacao = ""
	modos = {r["modo"]: r for r in resumo.get("comparativo_modos", [])}
	if ind["modo"] == '4-Inteligente' and '3-Solar e Bateria' in modos:
		economia = modos['3-Solar e Bateria']["custo_energia"] - ind["custo_energia"]
		comparacao = f"<b>R$ {numero_br(economia, 2)}</b> a menos que o modo 3 no mesmo dia"

	kpis = "".join([
		cartao_kpi("Recarga com energia renovável", f"{numero_br(ind['renovabilidade_pct'])}%",
			f"{numero_br(ind['energia_solar_kwh'])} kWh solar + {numero_br(ind['energia_bateria_kwh'])} kWh bateria", heroi=True),
		cartao_kpi("Energia entregue aos EVs", f"{numero_br(ind['energia_entregue_kwh'])} kWh",
			f"{ind['sessoes']} sessões · {ind['nao_atendidos']} na fila"),
		cartao_kpi("Margem líquida do dia", f"R$ {numero_br(ind['margem_liquida'], 2)}",
			f"receita R$ {numero_br(ind['receita_bruta'], 2)}"),
		cartao_kpi("Custo de energia da rede", f"R$ {numero_br(ind['custo_energia'], 2)}",
			comparacao or f"{numero_br(ind['energia_rede_ponta_kwh'])} kWh comprados na ponta")
	])
	kpis2 = "".join([
		cartao_kpi("CO₂ evitado vs. rede", f"{numero_br(ind['co2_evitado_kg'], 1)} kg",
			f"{numero_br(ind['co2_evitado_vs_combustao_kg'], 0)} kg vs. carros a combustão"),
		cartao_kpi("Autoconsumo fotovoltaico", f"{numero_br(ind['autoconsumo_fv_pct'])}%",
			f"{numero_br(ind['geracao_fv_kwh'])} kWh gerados"),
		cartao_kpi("Tempo de EVs parados", f"{ind['minutos_pausados']} min", "sem energia disponível"),
		cartao_kpi("Decisões automáticas do EMS", f"{ind['eventos_automacao']}", "comandos, ajustes e previsões")
	])

	secao_benchmark = ""
	if "benchmark" in graficos:
		b = resumo["benchmark"]
		secao_benchmark = f"""
<div class="cartao"><h2>Resultado em {b['dias']} dias simulados (clima e demanda variáveis)</h2>
<p class="sub">Mesma usina, mesmos veículos e mesmo clima para os quatro modos em cada dia — só a estratégia do EMS muda.
Modo 4 em destaque. O modo 4 teve margem ≥ modo 3 em {b['dias_modo4_melhor_margem_que_modo3']} de {b['dias']} dias.</p>
{graficos['benchmark']}
<details><summary>Ver tabela</summary>{tabela_modos(b['medias'])}</details></div>"""

	secao_comparativo = ""
	if "comparativo" in graficos:
		secao_comparativo = f"""
<div class="cartao"><h2>Comparativo dos modos neste dia</h2>
<p class="sub">Mesmo clima e mesma fila de veículos simulados com cada estratégia.</p>
{graficos['comparativo']}
<details><summary>Ver tabela</summary>{tabela_modos(resumo['comparativo_modos'])}</details></div>"""

	sessoes = tabela(["#", "Chegada", "Fim", "Modelo", "Meta", "kWh", "Solar %", "Preço R$/kWh", "Valor R$", "Pagamento"],
		[[s["id"], s["horario_chegada"], s["horario_fim"], s["modelo"], s["tipo_carregamento_meta"],
			numero_br(s["kwh_entregue"], 2), numero_br(s["percentual_renovavel"], 0), numero_br(s["preco_aplicado"], 2),
			numero_br(s["valor_cobrado"], 2), s["metodo_de_pagamento"]] for s in resumo["sessoes"]])
	_, potencia, _, horas, fontes = preparar_series(resumo, CORES_CSS)
	tabela_horaria = tabela(["Hora", "Solar kWh", "Bateria kWh", "Rede kWh"],
		[[h, numero_br(fontes[0]["valores"][i], 2), numero_br(fontes[1]["valores"][i], 2),
			numero_br(fontes[2]["valores"][i], 2)] for i, h in enumerate(horas)])
	log = "\n".join(f"[{e['horario']}] {e['origem']:<10} {e['categoria']:<9} {e['mensagem']}" for e in resumo["eventos"])

	pagina = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ChargeGrid Intelligence — Dashboard do eletroposto GoodWe</title><style>{ESTILO}</style></head>
<body><div class="viz-root">
<div class="topo"><div><h1>ChargeGrid Intelligence — Eletroposto GoodWe</h1>
<p class="sub">{esc(cfg['modo_de_carregamento'])} · FV {numero_br(cfg['potencia_pico_kwp'])} kWp · inversor híbrido
{cfg['capacidade_inversor_kw']} kW · bateria {cfg['capacidade_bateria_kwh']} kWh · {cfg['pontos_de_recarga']}x
{esc(cfg['carregador']['modelo'])} · expediente {esc(cfg['horario_de_funcionamento'])} · gerado em {esc(resumo['gerado_em'])}</p></div>
<button id="tema" type="button">Alternar tema claro/escuro</button></div>
<div class="grade">
<div class="kpis">{kpis}</div>
<div class="kpis">{kpis2}</div>
<div class="cartao weely"><h2>Weely — leitura automática do dia</h2>{''.join(f'<p>{esc(t)}</p>' for t in insights)}</div>
<div class="cartao"><h2>Fluxo de potência ao longo do dia</h2>
<p class="sub">Passe o mouse para ver os valores a cada 5 minutos.</p>{graficos['potencia']}</div>
<div class="cartao"><h2>Bateria: estado de carga e reserva planejada</h2>
<p class="sub">O EMS preditivo guarda energia para a ponta; depois das 18h o piso é liberado.</p>{graficos['bateria']}</div>
<div class="cartao"><h2>De onde veio a energia de cada hora</h2>
<p class="sub">kWh entregues aos veículos por fonte.</p>{graficos['fontes']}
<details><summary>Ver tabela</summary>{tabela_horaria}</details></div>
{secao_comparativo}
{secao_benchmark}
<div class="cartao"><h2>Sessões de recarga</h2>{sessoes}</div>
<div class="cartao"><h2>Log de automação ({len(resumo['eventos'])} eventos)</h2><pre class="log">{esc(log)}</pre></div>
</div></div><div id="dica" role="tooltip"></div><script>{SCRIPT}</script></body></html>"""
	with open(caminho, "w", encoding="utf-8") as arquivo:
		arquivo.write(pagina)
	return caminho


if __name__ == "__main__":
	analisador = argparse.ArgumentParser(description="Gera o dashboard HTML e os SVGs a partir de um resumo JSON")
	analisador.add_argument("resumo", help="arquivo resumo_*.json exportado pelo simulador")
	analisador.add_argument("--html", default=None, help="caminho do HTML (padrão: ao lado do JSON)")
	analisador.add_argument("--svg", default=None, help="pasta para exportar os gráficos em SVG")
	argumentos = analisador.parse_args()
	with open(argumentos.resumo, encoding="utf-8") as arquivo:
		dados = json.load(arquivo)
	destino = argumentos.html or argumentos.resumo.replace("resumo_", "dashboard_").replace(".json", ".html")
	print("Dashboard:", gerar_dashboard(dados, destino))
	if argumentos.svg:
		for caminho_svg in exportar_svgs(dados, argumentos.svg):
			print("SVG:", caminho_svg)
