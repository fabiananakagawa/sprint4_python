# ROTEIRO OBJETIVO — VÍDEO SPRINT 4 (≈ 4min30)

ChargeGrid Intelligence · Eletroposto Inteligente GoodWe

Janelas que precisam estar abertas antes de apertar REC:
- [A] Navegador, aba 1: README no GitHub — https://github.com/fabiananakagawa/sprint4_python
- [B] Navegador, aba 2: dashboard — dados_exemplo/dashboard_demo.html
- [C] Terminal PowerShell na pasta do projeto (comando abaixo, ainda sem executar)
- Este roteiro (fora da área gravada)

Comando da demonstração (digitar na CENA 3):
    python "Programa de Recarga GoodWe.py" --auto --seed 22 --dias 30 --weely

=====================================================================

## CENA 1 · 0:00–0:35 · ABERTURA — André

GRAVAR:
1. Janela [A], topo do README (título + imagem do dashboard).
2. Rolar devagar até a tabela "Equipe".

FALAR:
"Olá! Somos a equipe ChargeGrid e este é o nosso eletroposto inteligente
para o desafio GoodWe. Ele resolve três problemas: o carro carrega no
horário de ponta, quando a energia é mais cara; carregar com energia da
rede nesse horário reduz o ganho ambiental; e o carro fica parado quando
o sol acaba."

=====================================================================

## CENA 2 · 0:35–1:10 · ARQUITETURA GOODWE — Bruno

GRAVAR:
1. Em [A], rolar até "3.1 Diagrama de blocos".
2. Passar o mouse em: Inversor híbrido → Banco de baterias → Medidor →
   Carregadores HCA-G2 → EMS.

FALAR:
"O inversor híbrido GoodWe junta energia solar, bateria e rede. A
bateria guarda a sobra do meio-dia. O medidor inteligente dá prioridade
ao prédio. Os carregadores HCA-G2 recebem o comando de potência. E o nosso
controlador, o EMS, decide tudo a cada cinco minutos."

=====================================================================

## CENA 3 · 1:10–1:55 · SISTEMA RODANDO + EMS INTELIGENTE — Fabiana

GRAVAR:
1. Ir para [C], digitar o comando e apertar Enter.
2. Esperar terminar (≈ 10 s). A Weely vai abrir: NÃO digitar nada ainda.
3. Rolar para cima até "LOG DE AUTOMAÇÃO".
4. Ir para [B] e rolar até o gráfico "Bateria: estado de carga e reserva
   planejada". Apontar com o mouse a linha cinza e a marca das 18h.

FALAR:
"Este é o sistema rodando um dia completo. O diferencial da Sprint 4 é o
modo inteligente: ele aprende quanto o céu está nublado, prevê a demanda e
guarda bateria para as seis da tarde, quando a energia é mais cara. A linha
cinza é a reserva calculada; às dezoito horas ela é liberada e a bateria
assume. E todo carro recebe uma potência mínima: nenhum fica parado."

=====================================================================

## CENA 4 · 1:55–2:40 · RESULTADOS — Iago

GRAVAR:
1. Em [B], rolar até "Resultado em 30 dias simulados".
2. Apontar com o mouse a barra azul (modo 4) em "Compra no horário de
   ponta" e depois em "Tempo de EVs parados".

FALAR:
"Simulamos trinta dias com clima e demanda diferentes, e os quatro modos
enfrentam as mesmas condições. Comparado à Sprint 3, o modo inteligente
compra sessenta e sete por cento menos energia na ponta, gasta vinte e
cinco por cento menos com a rede e zera o tempo de carros parados.
Comparado a um eletroposto comum, a recarga vai de trinta e um para
setenta e cinco por cento renovável."

=====================================================================

## CENA 5 · 2:40–3:40 · DASHBOARD + WEELY — João Pedro

GRAVAR:
1. Em [B], subir para o topo (Home). Mostrar os cartões de indicadores.
2. Passar o mouse no gráfico "Fluxo de potência" (aparece o tooltip).
3. Clicar em "Alternar tema claro/escuro" e clicar de novo.
4. Ir para [C] e digitar, um de cada vez:
     como foi o dia?
     o que você recomenda?
     sair

FALAR:
"Os dados viram um dashboard que abre em qualquer navegador, com gráficos
interativos e modo escuro. E criamos a Weely, nossa assistente virtual,
que responde em português usando os dados do dia. Ela viu que cinco
clientes foram embora sem carregar, calculou a receita perdida e
recomendou mais um conector."

=====================================================================

## CENA 6 · 3:40–4:30 · SUSTENTABILIDADE E FECHAMENTO — Kayky

GRAVAR:
1. Ir para [A] e rolar até "8. Avaliação crítica".
2. No fim da fala, rolar até "10. Estrutura do repositório".

FALAR:
"No Brasil a energia da rede já é limpa, então o maior ganho ambiental é
trocar carros a combustão por elétricos sem sobrecarregar a rede na
ponta. Sobre os limites: os dados são simulados e a conexão com o
inversor real ainda precisa ser testada em campo. Código, testes e
documentação estão no repositório. Obrigado!"

=====================================================================

## SE ALGO DER ERRADO
- O terminal travou ou deu erro? Abra dados_exemplo/execucao_demonstracao.txt
  e mostre a mesma execução.
- Passou de 5 minutos? Corte a CENA 2 pela metade.
- Os números são sempre os mesmos porque o comando usa --seed 22.

## DEPOIS DE GRAVAR
1. YouTube → Enviar vídeo → Visibilidade: NÃO LISTADO.
2. Colar o link em "SPRINT 4 - Entrega ChargeGrid.txt" (no lugar de
   COLE_AQUI_O_LINK_DO_VIDEO) e entregar esse .txt.
