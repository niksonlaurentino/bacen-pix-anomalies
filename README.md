Detecção de Anomalias em Transações PIX (Dados BACEN)
Projeto que baixa dados públicos de transações PIX diretamente da API do Banco Central do Brasil (BACEN), realiza engenharia de atributos e utiliza um modelo Isolation Forest (scikit-learn) para detectar contas com comportamento financeiro atípico (possíveis anomalias/fraudes), com visualizações interativas via matplotlib/seaborn.
📋 Sumário
•	Estrutura do projeto
•	Requisitos
•	Instalação
•	Como usar
•	Exemplos de uso
•	Saídas geradas
•	Observações e limitações
•	Licença
🗂️ Estrutura do projeto
.
├── API_BACEN_data_download.py   # Módulo de extração de dados via API OData do BACEN
├── Main.py                      # Pipeline de engenharia de atributos, modelagem e visualização
└── dados_pix_selecionado.csv    # Gerado automaticamente após o download (não versionar)
•	API_BACEN_data_download.py: expõe a função baixar_dados_bacen(), que solicita interativamente (via terminal) o ano, mês e quantidade de linhas desejadas, consulta o endpoint CnaePorteRecebedor da API pública do BACEN e salva o resultado em dados_pix_selecionado.csv.
•	Main.py: importa o módulo acima, executa o download, carrega o CSV gerado, aplica engenharia de atributos (volume por pagador, ticket médio, ratios, transformações logarítmicas), treina um IsolationForest para detectar anomalias e exibe painéis gráficos com os resultados.
✅ Requisitos
•	Python 3.9+
•	Conexão com a internet (para consultar a API do BACEN)
•	Bibliotecas Python: 
o	pandas
o	numpy
o	requests
o	scikit-learn
o	matplotlib
o	seaborn
🚀 Instalação
1.	Clone o repositório:
bash
   git clone https://github.com/seu-usuario/anomalias-pix-bacen.git
   cd anomalias-pix-bacen
2.	(Opcional, mas recomendado) Crie um ambiente virtual:
bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
3.	Instale as dependências:
bash
   pip install pandas numpy requests scikit-learn matplotlib seaborn
Ou crie um arquivo requirements.txt com o conteúdo abaixo e instale com pip install -r requirements.txt:
   pandas>=1.5.0
   numpy>=1.23.0
   requests>=2.28.0
   scikit-learn>=1.2.0
   matplotlib>=3.6.0
   seaborn>=0.12.0
🖥️ Como usar
Basta executar o script principal:
bash
python Main.py
Durante a execução, o terminal solicitará interativamente as seguintes informações (definidas em API_BACEN_data_download.py):
1.	Ano de partida para o extrato (formato YYYY, até o ano atual).
2.	Mês de início do extrato (a faixa de meses válidos depende do ano informado).
3.	Quantidade de linhas a baixar por arquivo (mínimo 100, máximo 10.000).
Após o download, o script:
1.	Salva os dados em dados_pix_selecionado.csv.
2.	Remove colunas com muitos valores nulos (vlcompra, vldinespec, se presentes).
3.	Divide os dados em treino/teste (80/20).
4.	Cria atributos derivados (ex.: log_vol_por_pagador, log_ticket_medio, ratio_pag_rec).
5.	Normaliza os dados com StandardScaler.
6.	Treina um IsolationForest (contaminação de 1%) para identificar anomalias.
7.	Imprime no console as 10 anomalias mais severas e uma comparação entre pequenos negócios/pessoas físicas e demais portes.
8.	Exibe dois painéis gráficos (scatter plot, gráfico de barras por porte, histograma de score, top 10 anomalias e gráfico de rosca de composição de risco).
💡 Exemplos de uso
Executando o pipeline completo (interativo)
bash
python Main.py
Exemplo de interação no terminal:
Qual será ano de ponto de partida para solicitar extrato? (YYYY): 2024
Ano selecionado: 2024
Digite o número do mês de início do extrato (1 a 8): 3
Quantas linhas para baixar por arquivo? (MIN 100, MAX 10000): 5000
Testando apenas o módulo de extração de dados
O módulo API_BACEN_data_download.py pode ser executado isoladamente para validar a extração, sem rodar o pipeline de modelagem:
bash
python API_BACEN_data_download.py
Importando a função de download em outro script
python
import API_BACEN_data_download as bacen

df = bacen.baixar_dados_bacen()  # solicitará ano, mês e nº de linhas via input()
print(df.head())
📊 Saídas geradas
•	dados_pix_selecionado.csv: dados brutos baixados da API do BACEN para o período solicitado.
•	Console: total de registros, top 10 anomalias mais severas (com valores formatados em R$), e proporção de alertas por porte.
•	Gráficos (via plt.show()): 
o	Painel 1: scatter plot (escala log) de quantidade de lançamentos vs. volume líquido, barras de anomalias por porte e histograma da distribuição do score de anomalia.
o	Painel 2: barras com as top 10 anomalias por volume (em bilhões de R$) e gráfico de rosca com a composição de risco (Pessoa Física/Microempresa vs. demais portes).
⚠️ Observações e limitações
•	O script API_BACEN_data_download.py depende de entrada manual via terminal (input()), portanto não é adequado para execução totalmente automatizada/agendada sem adaptações.
•	O endpoint consultado é o CnaePorteRecebedor da API OData pública do BACEN; instabilidades ou mudanças no serviço podem afetar o download.
•	O modelo IsolationForest é treinado com uma taxa de contaminação fixa de 1% (contamination=0.01); ajuste esse parâmetro conforme a base de dados utilizada.
•	Recomenda-se não versionar o arquivo dados_pix_selecionado.csv no Git, adicionando-o ao .gitignore.
📄 Licença
Este projeto está licenciado sob os termos da licença MIT. Sinta-se livre para usar, modificar e distribuir.

