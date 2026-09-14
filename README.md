# Detecção de Anomalias em Transações Pix (BACEN)

Projeto para **detecção de anomalias em transações Pix** a partir de dados públicos do Banco Central do Brasil (BACEN). O pipeline baixa dados abertos do Pix via API OData do BACEN, realiza engenharia de atributos e treina um modelo não supervisionado (`IsolationForest`) para identificar transações financeiras atípicas, com visualizações gráficas dos resultados.

## 📁 Estrutura do Projeto

```
.
├── API_BACEN_data_download.py   # Módulo de extração de dados do Pix via API do BACEN
├── main.py                      # Pipeline de engenharia de atributos, treino e detecção de anomalias
├── requirements.txt              # Dependências do projeto
└── README.md                     # Este arquivo
```

> O script `main.py` importa e executa `API_BACEN_data_download.py` automaticamente, gerando o arquivo `dados_pix_selecionado.csv` que é consumido em seguida pelo pipeline de análise.

## ✅ Requisitos

- Python **3.9** ou superior
- Acesso à internet (para consultar a API pública do BACEN em `olinda.bcb.gov.br`)
- Bibliotecas listadas em `requirements.txt`:
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn`
  - `scikit-learn`
  - `requests`

## 🚀 Instalação

1. **Clone o repositório**

   ```bash
   git clone https://github.com/seu-usuario/pix-anomaly-detection.git
   cd pix-anomaly-detection
   ```

2. **Crie e ative um ambiente virtual** (recomendado)

   ```bash
   python -m venv venv

   # Linux / macOS
   source venv/bin/activate

   # Windows
   venv\Scripts\activate
   ```

3. **Instale as dependências**

   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Como usar

### 1. Executar o pipeline completo

Basta rodar o script principal. Ele fará o download dos dados, o pré-processamento, o treinamento do modelo e exibirá os gráficos de anomalias:

```bash
python main.py
```

Durante a execução, você será solicitado a informar interativamente (via terminal):

```text
Qual será ano de ponto de partida para solicitar extrato? (YYYY): 2024
Digite o número do mês de início do extrato (1 a 12): 6
Quantas linhas para baixar por arquivo? (MIN 100, MAX 10000): 5000
```

Ao final, o script imprime um resumo das anomalias detectadas e abre três painéis gráficos:

- Dispersão em escala logarítmica (volume x quantidade de lançamentos), colorida por status de anomalia;
- Barras com a contagem de anomalias por porte da empresa recebedora;
- Histograma da distribuição do score de anomalia, com o limiar de decisão destacado;
- Top 10 anomalias mais severas e gráfico de rosca com a proporção de risco (PF/Microempresa vs. demais portes).

### 2. Baixar os dados isoladamente

Caso você queira apenas testar a extração de dados do BACEN, sem rodar todo o pipeline de análise:

```bash
python API_BACEN_data_download.py
```

Isso gera (ou sobrescreve) o arquivo `dados_pix_selecionado.csv` no diretório atual, exibindo as primeiras linhas do DataFrame retornado.

### 3. Usar as funções em outro script Python

```python
import API_BACEN_data_download as bacen
from main import eng_atributes
import pandas as pd

# Baixa os dados interativamente e salva em dados_pix_selecionado.csv
df_mes = bacen.baixar_dados_bacen()

# Carrega os dados e aplica a engenharia de atributos
df = pd.read_csv("dados_pix_selecionado.csv")
features = eng_atributes(df)
print(features.head())
```

> ⚠️ Nota: `main.py`, no estado atual, executa o pipeline completo assim que é importado (não possui um bloco `if __name__ == "__main__":` isolando a execução). Para importar `eng_atributes` sem disparar todo o pipeline, considere refatorar `main.py` movendo a lógica de execução para dentro de uma função `main()` protegida por esse bloco.

## 📊 Fonte dos dados

Os dados são obtidos do serviço público **Pix Dados Abertos** do Banco Central do Brasil, endpoint `CnaePorteRecebedor`:

```
https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/CnaePorteRecebedor
```

## 🧠 Modelo utilizado

A detecção de anomalias é feita com [`IsolationForest`](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) (scikit-learn), configurado com `contamination=0.01` (assume-se que ~1% das transações no conjunto de teste sejam atípicas). As features de entrada são normalizadas com `StandardScaler` antes do treinamento.

