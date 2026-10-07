# Roteiro do vídeo técnico — Sprint 4 (até 5 minutos)

**Preparação antes de gravar**

- Terminal aberto na pasta do repositório, fonte grande, janela maximizada.
- `dados_exemplo/dashboard_demo.html` aberto no navegador (ou gerado ao vivo no passo 2).
- Comando pronto: `python "Programa de Recarga GoodWe.py" --auto --seed 22 --dias 30 --weely`

---

### 0:00 – 0:30 · Abertura e problema (tela: README, seção 1)

> "Somos a equipe ChargeGrid. Um eletroposto comercial tem três problemas: a recarga acontece no
> horário de ponta, quando a energia custa 70% mais; carregar com energia da rede reduz o ganho
> ambiental; e, quando a energia renovável acaba, o carro do cliente fica parado. Nossa solução integra
> o ecossistema GoodWe com um controlador inteligente para resolver os três."

### 0:30 – 1:15 · Arquitetura e tecnologias GoodWe (tela: diagrama de blocos do README)

> "O inversor híbrido GoodWe soma no mesmo barramento a energia solar, a bateria e a rede. Sem ele, a
> bateria não poderia alimentar os carregadores. O medidor inteligente garante que o prédio tenha
> prioridade. Os carregadores HCA-G2 executam o setpoint, e seus limites reais, como a modulação
> mínima de 4,2 kW, estão no código. Cada equipamento é um driver: o `integracao_goodwe.py` lê um
> inversor real pela rede local e entrega as mesmas grandezas ao EMS."

### 1:15 – 2:15 · Solução funcionando (tela: terminal executando o comando)

- Mostrar a configuração (58 kWp, 50 kW, 112 kWh, 2 × GW22K) e a telemetria correndo.
- Rolar até o **log de automação** e destacar as linhas `PREVISÃO`:

> "Este é o diferencial da Sprint 4: o EMS preditivo. Ele aprende a nebulosidade comparando a geração
> medida com a prevista, estima a demanda do horário de ponta e calcula quanto de bateria guardar.
> Às 18h a reserva é liberada e a bateria assume a recarga."

### 2:15 – 3:15 · Resultados (tela: comparativo e benchmark no terminal, depois o dashboard)

- Mostrar a tabela **COMPARATIVO DOS MODOS** e depois o **BENCHMARK de 30 dias**.

> "Para não depender de um dia favorável, simulamos 30 dias com clima e demanda diferentes. Em cada
> dia, os quatro modos enfrentam o mesmo clima e os mesmos carros. Comparado ao melhor modo da Sprint 3,
> o modo inteligente compra 67% menos energia na ponta, gasta 25% menos com a rede e zera o tempo de
> carros parados. Comparado a uma operação convencional, a recarga passa de 31% para 75% renovável,
> com 21 mil reais a mais de margem por ano."

- Abrir o dashboard: KPIs, gráfico de potência (passar o mouse para mostrar o tooltip), gráfico da
  bateria com o piso planejado, alternar modo claro/escuro.

### 3:15 – 4:15 · Assistente Weely (tela: terminal, conversa ao final da execução)

Perguntas sugeridas:

1. `como foi o dia?`
2. `quanto co2 eu evitei?`
3. `o que você recomenda?`
4. `qual o melhor horário para carregar?`

> "A Weely transforma os dados em decisões: ela detectou cinco clientes que foram embora sem
> carregar, estimou a receita perdida e recomendou mais um conector. Também viu sol sobrando e sugeriu
> desconto nesse horário."

### 4:15 – 5:00 · Sustentabilidade, limitações e fechamento (tela: README seção 8)

> "O maior ganho ambiental é substituir carros a combustão sem pressionar a rede na ponta, que é
> atendida por termelétricas. Somos transparentes sobre os limites: os dados são simulados e o
> adaptador GoodWe ainda precisa ser validado em um inversor físico. Em dias de demanda muito alta,
> guardar bateria pode reduzir a energia entregue. O código, os dados de exemplo, os testes e a
> documentação estão no repositório. Obrigado!"
