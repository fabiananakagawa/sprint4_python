# ROTEIRO OBJETIVO — VÍDEO SPRINT 4 (≈ 4min30)

ChargeGrid Intelligence · Eletroposto Inteligente GoodWe

Janelas que precisam estar abertas antes de apertar REC:
- [A] Navegador, aba 1: README no GitHub — https://github.com/fabiananakagawa/sprint4_python
- [B] Navegador, aba 2: dashboard — dados_exemplo/dashboard_demo.html
- [C] Terminal PowerShell na pasta do projeto (comando abaixo, ainda sem executar)
- Este roteiro (fora da área gravada)

Comando da demonstração (digitar na CENA 3):
    python "Programa de Recarga GoodWe.py" --auto --seed 22 --dias 30 --weely

Dica: não precisa decorar. Leia algumas vezes e fale com as suas palavras;
o importante é manter os números e a ideia de cada cena.

=====================================================================

## CENA 1 · 0:00–0:35 · ABERTURA — André

GRAVAR:
1. Janela [A], topo do README (título + imagem do dashboard).
2. Rolar devagar até a tabela "Equipe".

FALAR:
"Olá, pessoal! Eu sou o André e, junto com a minha equipe, vou apresentar
o ChargeGrid, o nosso projeto final para o desafio da GoodWe.
A gente partiu de uma situação bem comum: um estabelecimento instala
carregadores para carros elétricos e logo percebe três problemas. As
pessoas costumam carregar no fim da tarde, justamente no horário em que a
energia é mais cara. Usar a energia da rede nesse horário diminui o
benefício ambiental. E, quando o sol vai embora, o carro do cliente às
vezes fica parado, sem carregar. Foi isso que a gente decidiu resolver."

=====================================================================

## CENA 2 · 0:35–1:10 · ARQUITETURA GOODWE — Bruno

GRAVAR:
1. Em [A], rolar até "3.1 Diagrama de blocos".
2. Passar o mouse em: Inversor híbrido → Banco de baterias → Medidor →
   Carregadores HCA-G2 → EMS.

FALAR:
"Eu sou o Bruno e vou mostrar como o sistema está montado. O coração dele
é o inversor híbrido da GoodWe, que consegue juntar num só lugar a energia
dos painéis solares, a da bateria e a da rede. A bateria guarda o que sobra
de energia no meio do dia. O medidor inteligente garante que o prédio
sempre tenha prioridade. E os carregadores da linha HCA-G2 recebem as
ordens de quanta potência entregar. Quem dá essas ordens é o nosso
controlador, o EMS, que reavalia tudo a cada cinco minutos."

=====================================================================

## CENA 3 · 1:10–1:55 · SISTEMA RODANDO + EMS INTELIGENTE — Fabiana

GRAVAR:
1. Ir para [C], digitar o comando e apertar Enter.
2. Esperar terminar (≈ 10 s). A Weely vai abrir: NÃO digitar nada ainda.
3. Rolar para cima até "LOG DE AUTOMAÇÃO".
4. Ir para [B] e rolar até o gráfico "Bateria: estado de carga e reserva
   planejada". Apontar com o mouse a linha cinza e a marca das 18h.

FALAR:
"Eu sou a Fabiana. Aqui o sistema está simulando um dia inteiro de
funcionamento. Na sprint anterior, a gente notou que a bateria
descarregava cedo demais e chegava vazia às seis da tarde, que é quando a
energia fica mais cara. Por isso, nesta sprint, criamos o modo
inteligente. Ele vai aprendendo durante o dia o quanto o céu está nublado,
estima quanta energia os carros vão precisar e decide quanto de bateria
guardar. Nesse gráfico, a linha cinza é essa reserva. Às dezoito horas
ela é liberada e a bateria passa a abastecer os carros. Além disso, todo
carro conectado recebe sempre uma potência mínima, então ninguém fica
esperando."

=====================================================================

## CENA 4 · 1:55–2:40 · RESULTADOS — Iago

GRAVAR:
1. Em [B], rolar até "Resultado em 30 dias simulados".
2. Apontar com o mouse a barra azul (modo 4) em "Compra no horário de
   ponta" e depois em "Tempo de EVs parados".

FALAR:
"Eu sou o Iago e vou falar dos resultados. Para não depender de um dia
que desse certo por sorte, a gente simulou trinta dias com clima e
movimento diferentes. Em cada dia, os quatro modos passam exatamente pelas
mesmas condições, então a comparação é justa. Em relação ao melhor modo
da sprint passada, o modo inteligente comprou sessenta e sete por cento
menos energia no horário de ponta, gastou vinte e cinco por cento menos
com a conta de luz e acabou com o tempo de carro parado. E, comparando
com um eletroposto comum, a parte renovável da recarga sobe de trinta e um
para setenta e cinco por cento."

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
"Eu sou o João Pedro. A gente também se preocupou em deixar tudo fácil de
entender para o dono do estabelecimento, que nem sempre é da área técnica.
Todos os dados aparecem neste painel, que abre direto no navegador. Dá
para passar o mouse nos gráficos para ver os valores e ainda trocar para
o modo escuro. Também criamos a Weely, uma assistente virtual. É só
perguntar em português. Aqui, por exemplo, ela percebeu que cinco clientes
foram embora sem conseguir carregar, calculou quanto isso representou em
receita e sugeriu instalar mais um carregador."

=====================================================================

## CENA 6 · 3:40–4:30 · SUSTENTABILIDADE E FECHAMENTO — Kayky

GRAVAR:
1. Ir para [A] e rolar até "8. Avaliação crítica".
2. No fim da fala, rolar até "10. Estrutura do repositório".

FALAR:
"Eu sou o Kayky e vou fechar a apresentação. Como a energia da rede no
Brasil já é bastante limpa, o maior ganho ambiental do projeto está em
ajudar a substituir carros a combustão por elétricos, sem sobrecarregar a
rede no horário de pico. A gente também quis ser transparente sobre os
limites: os dados ainda são simulados, e a conexão com um inversor real
precisa ser testada na prática. Todo o código, os testes e a documentação
estão no nosso repositório. Muito obrigado pela atenção!"

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
