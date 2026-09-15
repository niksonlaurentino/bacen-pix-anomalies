Aqui está uma versão do seu README.md reestruturada com scannability otimizada, padronização de formatação Markdown e hierarquia clara para repositórios do GitHub.
🚀 Detecção de Anomalias em Transações PIX (BACEN)
Pipeline completo em Python para extração de dados públicos de transações PIX diretamente da API do Banco Central do Brasil (BACEN), seguido de engenharia de atributos, detecção de comportamento financeiro atípico via Isolation Forest e visualização interativa de resultados.
📋 Sumário
•	Estrutura do Projeto
•	Requisitos
•	Instalação
•	Como Usar
•	Exemplos de Uso
•	Saídas Geradas
•	Observações e Limitações
•	Licença
🗂️ Estrutura do Projeto
Plaintext
.
├── API_BACEN_data_download.py   # Módulo de extração de dados via API OData do BACEN
├── Main.py                      # Pipeline de engenharia de atributos, ML e visualização
└── dados_pix_selecionado.csv    # Gerado automaticamente pelo download (não versionado)
Detalhamento dos Módulos
•	API_BACEN_data_download.py: Expõe a função baixar_dados_bacen(). Solicita parâmetros via terminal (ano, mês e volume de linhas), consulta o endpoint CnaePorteRecebedor do BACEN e salva o resultado em dados_pix_selecionado.csv.
•	Main.py: Gerencia a execução completa. Realiza o download dos dados, executa a limpeza, faz o tratamento e engenharia de variáveis, treina o modelo IsolationForest e gera painéis gráficos interativos.
✅ Requisitos
•	Python: 3.9 ou superior
•	Conexão com a internet para requisições à API pública do BACEN
Dependência	Versão Mínima
pandas	>= 1.5.0
numpy	>= 1.23.0
requests	>= 2.28.0
scikit-learn	>= 1.2.0
matplotlib	>= 3.6.0
seaborn	>= 0.12.0
🚀 Instalação
1.	Clone o repositório:
Bash
git clone https://github.com/seu-usuario/anomalias-pix-bacen.git
cd anomalias-pix-bacen
2.	Crie e ative um ambiente virtual (recomendado):
Bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
3.	Instale as dependências:
Bash
pip install pandas numpy requests scikit-learn matplotlib seaborn
Dica: Se optar por utilizar um arquivo requirements.txt, execute pip install -r requirements.txt.
🖥️ Como Usar
Execute o script principal para rodar o pipeline interativo de ponta a ponta:
Bash
python Main.py
Durante a execução, o terminal solicitará as seguintes entradas:
•	Ano de partida (formato YYYY, limitado ao ano atual)
•	Mês de início (numérico, dependendo do ano informado)
•	Quantidade de linhas por arquivo (mínimo 100, máximo 10.000)
Fluxo de Processamento Automático
•	Download & Limpeza: Salva os dados brutos e descarta colunas com alta vacuidade (vlcompra, vldinespec).
•	Feature Engineering: Divisão treino/teste (80/20), cálculo de métricas derivadas (escala logarítmica para volume e ticket médio, razão pagador/recebedor) e padronização com StandardScaler.
•	Modelagem: Treinamento do modelo IsolationForest com taxa de contaminação fixa de 1%.
•	Análise: Exibição das 10 principais anomalias no console e geração dos painéis visuais.
💡 Exemplos de Uso
Execução interativa padrão:
Bash
python Main.py
Exemplo de interação no terminal:
Plaintext
Qual será ano de ponto de partida para solicitar extrato? (YYYY): 2024
Ano selecionado: 2024
Digite o número do mês de início do extrato (1 a 8): 3
Quantas linhas para baixar por arquivo? (MIN 100, MAX 10000): 5000
Testando apenas o módulo de extração:
Bash
python API_BACEN_data_download.py
Importando o módulo em scripts externos:
Python
import API_BACEN_data_download as bacen

# Solicita os parâmetros interativamente e retorna um DataFrame
df = bacen.baixar_dados_bacen()
print(df.head())
📊 Saídas Geradas
•	dados_pix_selecionado.csv: Dataset bruto extraído do BACEN.
•	Console: Mapeamento do quantitativo de registros, listagem das 10 anomalias mais severas (com valores formatados em R$) e proporção de alertas segregados por porte de empresa.
•	Painéis Gráficos (matplotlib/seaborn):
o	Painel 1: Scatter plot em escala logarítmica (lançamentos vs. volume líquido), gráfico de barras de anomalias por porte e histograma dos scores de anomalia.
o	Painel 2: Ranking com as 10 maiores anomalias por volume financeiro e gráfico de rosca ilustrando a composição de risco.
⚠️ Observações e Limitações
•	Entrada Manual: A rotina do módulo API_BACEN_data_download.py utiliza input(), demandando adaptações para ser integrada a pipelines de agendamento automático (como Airflow ou Cron).
•	Estabilidade do Endpoint: O serviço consulta a API OData do BACEN (CnaePorteRecebedor), sujeito a variações de disponibilidade do órgão público.
•	Hiperparâmetros do Modelo: O parâmetro contamination=0.01 do IsolationForest assume uma taxa fixa de 1% de discrepâncias. É recomendável reavaliar esse parâmetro conforme o volume e o comportamento do conjunto de dados extraído.
•	Controle de Versão: É altamente recomendável incluir o arquivo dados_pix_selecionado.csv no .gitignore para evitar o commit de bases temporárias no repositório.
📄 Licença
Este projeto é distribuído sob os termos da licença MIT. Consulte o arquivo de licença para mais detalhes.

