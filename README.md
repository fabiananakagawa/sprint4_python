**Simulador de Operação de Eletropostos**
**Descrição do Projeto**

O simulador desenvolvido para a ChargeGrid Intelligence representa a primeira fundamentação técnica codificada do projeto, permitindo validar conceitos de gestão energética, carregamento veicular inteligente, precificação dinâmica e integração entre múltiplas fontes de energia.

A proposta do programa é simular o funcionamento operacional de um estabelecimento comercial que possui infraestrutura de carregamento veicular integrada a sistemas fotovoltaicos e carregadores inteligentes GoodWe.

O sistema realiza:

simulação de sessões de recarga;

cálculo de consumo energético;

balanceamento entre energia elétrica e energia solar;

análise operacional;

cálculo financeiro das recargas;

tarifação dinâmica baseada em horário;

geração de relatórios operacionais e financeiros.

A simulação foi concebida como base inicial para evolução futura da plataforma ChargeGrid Intelligence e da IA conversacional Weely.

**Objetivo da Simulação**

O principal objetivo do simulador é reproduzir cenários reais de operação de eletropostos comerciais, permitindo validar conceitos como:

utilização inteligente de energia solar;

redução de sobrecarga energética;

otimização de distribuição de potência;

monetização da operação de recarga;

geração de indicadores analíticos;

análise operacional de múltiplas sessões de carregamento.

O programa também serve como base para futuros módulos de analytics, telemetria e inteligência operacional da plataforma.

Estrutura do Código

O sistema foi organizado de forma modular e progressiva para facilitar manutenção, evolução e entendimento lógico do fluxo operacional.

**Índice Estrutural do Código**
ÍNDICE
Pré-configuração: importação de bibliotecas e funções de apoio

1. Configuração inicial do estabelecimento
1.1 Cenário de energia do estabelecimento
1.2 Modo de carregamento padrão
1.2.1 Geração e consumo de energia solar do estabelecimento
1.2.2 Verificação de excedente solar
1.3 Modelo de carregador GoodWe
1.4 Capacidade da Bateria e Inversor
1.5 Relatório do sistema de energia do estabelecimento
1.6 Potência final para o carregamento e fonte de energia proveniente

2. Precificação
2.1 Preço base por kWh
2.2.1 Horários de funcionamento
2.2.2 Faixa de horário com variável
2.2.2.3 Setup multiplicador variável
2.3 Cálculo de preço base + faixa de horário com variável

3. Relatório de configuração concluída

4. Simulação das sessões de recargas
4.1 Preparação do cenário de simulação
4.2 Simulação do dia em loop de carros

5. Relatório final
5.1 Relatório operacional
5.2 Relatório financeiro
   
**Principais Conceitos Simulados**

Gestão Energética Inteligente

O simulador avalia cenários de distribuição energética considerando:

energia proveniente da rede elétrica;
geração fotovoltaica;
disponibilidade energética;
potência máxima dos carregadores;
sessões simultâneas de recarga.

O objetivo é reproduzir a lógica operacional da ChargeGrid Intelligence no gerenciamento inteligente da infraestrutura.

Utilização de Energia Solar

O sistema realiza cálculos básicos de:

geração solar;
consumo do estabelecimento;
excedente fotovoltaico;
aproveitamento energético.

Isso permite validar cenários onde parte das sessões de recarga utiliza energia renovável gerada localmente.

**Precificação Dinâmica**

O simulador implementa uma lógica inicial de tarifação variável baseada em horário de funcionamento.

A estrutura considera:

preço base por kWh;
multiplicadores por faixa horária;
horários de pico;
cálculo automático do valor da sessão.

Essa lógica servirá como base futura para integração com a IA Weely e modelos mais avançados de recomendação de tarifas.

**Simulação Operacional**

Durante a execução, o sistema simula:

entrada de veículos;
sessões de carregamento;
consumo energético;
tempo de recarga;
potência utilizada;
faturamento gerado.

Os dados são utilizados para construção de relatórios operacionais e financeiros.

**Relatórios Gerados**
Relatório Operacional

Ao final da execução, o sistema apresenta indicadores como:

número total de recargas;
energia total consumida;
uso de energia solar;
potência média utilizada;
sessões simultâneas;
tempo médio de carregamento.
Relatório Financeiro

Também são gerados indicadores financeiros, incluindo:

receita total;
faturamento por sessão;
valor médio de recarga;
impacto da tarifação dinâmica;
estimativa de monetização da operação.
Tecnologias Utilizadas

O projeto foi desenvolvido utilizando:

Python;
lógica procedural;
simulação computacional;
fundamentos de análise de dados;
conceitos de gestão energética e mobilidade elétrica.

**Próximos Passos do Projeto**

As próximas evoluções previstas para a ChargeGrid Intelligence incluem:

integração com APIs reais de carregadores;
leitura de telemetria em tempo real;
dashboards analíticos;
integração multi-marca via OCPP;
balanceamento dinâmico avançado;
analytics operacional;
IA conversacional Weely;
manutenção preditiva;
recomendação inteligente de tarifação;
gestão energética adaptativa.

**Visão Estratégica do Projeto**

A ChargeGrid Intelligence busca transformar eletropostos em plataformas inteligentes de energia, dados e mobilidade elétrica.

Mais do que fornecer carregamento veicular, a proposta do projeto é criar um ecossistema integrado capaz de unir:

eficiência energética;
sustentabilidade;
analytics;
inteligência operacional;
monetização;
experiência do usuário.

O simulador representa a primeira etapa prática dessa visão tecnológica.
