# Roteiro do vídeo técnico — Sprint 4 (até 5 minutos)

**ChargeGrid Intelligence — Eletroposto Inteligente GoodWe**

A divisão de falas entre os integrantes é uma sugestão; troquem à vontade. Cada bloco tem cerca de
40 a 50 segundos de fala (≈ 100 palavras), somando cerca de 4min40s.

---

## Antes de gravar (checklist)

1. Abrir o terminal **na pasta do repositório**, com fonte grande (Ctrl + roda do mouse) e janela maximizada.
2. Deixar pronto, sem executar, o comando:
   ```
   python "Programa de Recarga GoodWe.py" --auto --seed 22 --dias 30 --weely
   ```
3. Abrir no navegador, em abas separadas:
   - o README do GitHub: <https://github.com/fabiananakagawa/sprint4_python>
   - o dashboard: `dados_exemplo/dashboard_demo.html` (duplo clique no arquivo)
4. Gravar a tela com o OBS Studio ou com a Barra de Jogos do Windows (Win + Alt + R). Cada integrante
   pode gravar o próprio áudio, e as partes são juntadas depois.
5. Publicar no YouTube como **Não listado** e colar o link no arquivo de entrega.

---

## Bloco 1 — Abertura e problema · 0:00 a 0:40
**Quem fala:** André · **Tela:** README no GitHub, com o print do dashboard no topo

> "Olá, somos a equipe ChargeGrid e este é o nosso projeto final para o desafio GoodWe: um eletroposto
> inteligente. Quem instala carregadores de carro elétrico enfrenta três problemas. Primeiro, o custo:
> os clientes carregam no fim da tarde, que é o horário de ponta, quando a energia da concessionária
> custa até setenta por cento mais. Segundo, a sustentabilidade: carregar com energia comprada da rede
> nesse horário reduz o ganho ambiental do carro elétrico. Terceiro, a experiência do cliente: quando a
> energia solar acaba, o carro fica parado no carregador. A nossa solução resolve os três problemas."

---

## Bloco 2 — Arquitetura e tecnologias GoodWe · 0:40 a 1:25
**Quem fala:** Bruno · **Tela:** README, seção 3.1 (diagrama de blocos); passe o mouse sobre cada bloco enquanto fala

> "A arquitetura junta os equipamentos GoodWe. O inversor híbrido é o centro: ele soma no mesmo
> barramento a energia solar, a bateria e a rede. Sem ele, a bateria não conseguiria alimentar os
> carregadores. O banco de baterias guarda a sobra do meio-dia. O medidor inteligente mede o consumo do
> prédio, que sempre tem prioridade. E os carregadores da Linha HCA-G2 recebem o comando de potência;
> os limites reais deles, como a potência mínima de 4,2 quilowatts, estão no código. Por cima disso
> roda o nosso controlador, o EMS, que decide tudo a cada cinco minutos."

---

## Bloco 3 — O diferencial: EMS preditivo · 1:25 a 2:15
**Quem fala:** Fabiana · **Tela:** execute o comando no terminal; quando terminar, role até o **LOG DE AUTOMAÇÃO** e depois abra o dashboard no gráfico **"Bateria: estado de carga e reserva planejada"**

> "Na Sprint 3, a bateria descarregava assim que o sol diminuía e chegava vazia às seis da tarde,
> justamente quando a energia é mais cara. Na Sprint 4, criamos o modo inteligente, que olha para a
> frente. Ele compara a geração medida com a prevista e aprende quanto o céu está nublado. Também
> aprende quanta potência os carros estão usando. Com isso, calcula quanta bateria guardar para o
> horário de ponta. No gráfico, a linha verde é a carga da bateria e a cinza é a reserva calculada:
> a bateria não desce abaixo dela antes das dezoito horas. Às dezoito a reserva é liberada e a bateria
> assume. Além disso, todo carro recebe uma potência mínima garantida, então nenhum fica parado."

---

## Bloco 4 — Resultados · 2:15 a 3:05
**Quem fala:** Iago · **Tela:** no terminal, a tabela **BENCHMARK — MÉDIA DE 30 DIAS**; depois o dashboard, na seção **"Resultado em 30 dias simulados"**

> "Para provar o ganho sem escolher um dia favorável, simulamos trinta dias com clima e demanda
> diferentes. Em cada dia, os quatro modos enfrentam o mesmo sol e os mesmos carros; só muda a
> estratégia. Comparado ao melhor modo da Sprint 3, o modo inteligente compra sessenta e sete por cento
> menos energia na ponta, gasta vinte e cinco por cento menos com a rede e zera o tempo de carros
> parados, que antes era de oitenta e um minutos por dia. Comparado a um eletroposto comum, a recarga
> passa de trinta e um para setenta e cinco por cento renovável, com cerca de vinte e dois mil reais a
> mais de margem por ano, usando o mesmo equipamento."

---

## Bloco 5 — Dashboard e assistente Weely · 3:05 a 4:00
**Quem fala:** João Pedro · **Tela:** dashboard (topo): mostre os indicadores, passe o mouse no gráfico de potência para aparecer o tooltip e clique em "Alternar tema". Depois volte ao terminal e converse com a Weely

Perguntas para digitar na Weely, nesta ordem:
1. `como foi o dia?`
2. `o que você recomenda?`
3. `qual o melhor horário para carregar?`
4. `sair`

> "Os dados viram um dashboard que abre em qualquer navegador, com os indicadores principais, gráficos
> interativos e modo escuro. E, para quem não é engenheiro, criamos a Weely, uma assistente virtual.
> Ela responde em português usando os dados reais do dia. Vejam: ela percebeu que cinco clientes foram
> embora sem carregar, calculou a receita perdida e recomendou mais um conector. Também viu sol sobrando
> à tarde e sugeriu um desconto nesse horário para atrair mais clientes."

---

## Bloco 6 — Sustentabilidade, limitações e encerramento · 4:00 a 4:45
**Quem fala:** Kayky · **Tela:** README, seção 8 (Avaliação crítica) e, no final, a seção 10 (estrutura do repositório)

> "Sobre sustentabilidade: como a matriz elétrica brasileira já é limpa, o maior ganho ambiental vem de
> substituir carros a combustão, e o nosso sistema faz isso sem sobrecarregar a rede no horário de
> ponta. Também somos transparentes sobre os limites: os dados são simulados, o adaptador para o inversor
> GoodWe real ainda precisa ser testado em campo e, em dias de demanda muito alta, guardar bateria pode
> reduzir a energia entregue. Todo o código, os testes automatizados, os dados de exemplo e a
> documentação estão no nosso repositório. Obrigado!"

---

## Dicas de gravação

- Falem devagar: o tempo acima já considera um ritmo calmo. Se passar de 5 minutos, encurtem o Bloco 2.
- Rodem o comando uma vez antes de gravar, para saber onde cada tabela aparece no terminal.
- O comando com `--seed 22` sempre produz os mesmos números citados no roteiro.
- Se a demonstração ao vivo der problema, usem `dados_exemplo/execucao_demonstracao.txt` e o
  `dashboard_demo.html`, que já mostram a mesma execução.
