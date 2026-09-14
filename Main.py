import API_BACEN_data_download as bacen
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Download e carga dos dados
bacen.baixar_dados_bacen()
df = pd.read_csv('dados_pix_selecionado.csv')

print("\n--- CONTINUANDO O SCRIPT MAIN.PY ---")
print("\n--- DADOS RECEBIDOS COM SUCESSO ---")
print(f"Total de registros: {len(df)}")

# Remoção de colunas com >90% nulos
cols_to_drop = [c for c in ['vlcompra', 'vldinespec'] if c in df.columns]
if cols_to_drop:
    df = df.drop(columns=cols_to_drop)

# 1. DIVISÃO TREINO E TESTE
df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

# 2. ENGENHARIA DE ATRIBUTOS
def eng_atributes(df_input):
    df_transformed = df_input.copy()
    
    # Mapeamento de porte (Não Informado alterado para peso 20)
    porte_peso = {
        'PESSOA FÍSICA': 1,
        'Microempresa': 2,
        'Pequeno Porte': 5,
        'Demais': 20,
        'Não Informado': 20
    }
    df_transformed['peso_porte'] = df_transformed['porte'].map(porte_peso).fillna(20)
    
    # Volume relativo por pagador
    df_transformed['vol_por_pagador'] = df_transformed['vllanliq'] / np.where(df_transformed['qtpagador'] < 1, 1, df_transformed['qtpagador'])
    df_transformed['log_vol_por_pagador'] = np.log1p(df_transformed['vol_por_pagador'])
    
    # Ratio vol/porte
    df_transformed['ratio_vol_porte'] = df_transformed['vol_por_pagador'] / df_transformed['peso_porte']
    df_transformed['log_ratio_vol_porte'] = np.log1p(df_transformed['ratio_vol_porte'])
    
    # Ticket médio
    df_transformed['ticket_medio'] = df_transformed['vllanliq'] / np.where(df_transformed['qtlanliq'] < 1, 1, df_transformed['qtlanliq'])
    df_transformed['log_ticket_medio'] = np.log1p(df_transformed['ticket_medio'])
    
    # Ratio pag/rec
    df_transformed['ratio_pag_rec'] = df_transformed['qtpagador'] / np.where(df_transformed['qtrecebedor'] < 1, 1, df_transformed['qtrecebedor'])
    df_transformed['log_ratio_pag_rec'] = np.log1p(df_transformed['ratio_pag_rec'])
    
    # Outros logs
    df_transformed['log_qtlanliq'] = np.log1p(df_transformed['qtlanliq'])
    
    features = [
        'log_vol_por_pagador', 
        'log_ratio_vol_porte', 
        'log_ratio_pag_rec', 
        'log_ticket_medio',
        'qtpagador', 
        'qtrecebedor',
        'log_qtlanliq'
    ]

    return df_transformed[features].fillna(0)

# 3. APLICAR ENGENHARIA DE ATRIBUTOS
X_train = eng_atributes(df_train)
X_test = eng_atributes(df_test)

# 4. NORMALIZAÇÃO
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 5. TREINAMENTO
iso_forest = IsolationForest(contamination=0.01, random_state=42)
iso_forest.fit(X_train_scaled)

# 6. PREDIÇÃO
df_test = df_test.copy()
df_test['target_anomalia'] = iso_forest.predict(X_test_scaled)
df_test['score_anomalia'] = iso_forest.decision_function(X_test_scaled)

anomalias = df_test[df_test['target_anomalia'] == -1].sort_values(by='score_anomalia', ascending=True)
print(f"\nTotal de anomalias detectadas no Teste: {len(anomalias)}")

# 7. INSPEÇÃO FORMATADA DOS OUTLIERS
cols_analise = ['porte', 'vllanliq', 'qtlanliq', 'qtpagador', 'qtrecebedor', 'score_anomalia']

df_print = anomalias[cols_analise].head(10).copy()
df_print['vllanliq'] = df_print['vllanliq'].apply(lambda x: f"R$ {x:,.2f}")
df_print['score_anomalia'] = df_print['score_anomalia'].apply(lambda x: f"{x:.4f}")

print("\n--- TOP 10 ANOMALIAS MAIS SEVERAS (POR SCORE) ---")
print(df_print)

pequenos_suspeitos = anomalias[anomalias['porte'].isin(['PESSOA FÍSICA', 'Microempresa'])]
print(f"\nDos {len(anomalias)} alertas, {len(pequenos_suspeitos)} são estritamente Pessoas Físicas ou Microempresas.")

# 8. PAINEL DE AVALIAÇÃO DO MODELO
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axes = plt.subplots(1, 3, figsize=(20, 5))

# Scatter Plot Log
sns.scatterplot(
    data=df_test, x='qtlanliq', y='vllanliq', hue='target_anomalia', 
    palette={1: '#2ecc71', -1: '#e74c3c'}, style='target_anomalia',
    markers={1: 'o', -1: 'X'}, s=70, ax=axes[0]
)
axes[0].set_xscale('log')
axes[0].set_yscale('log')
axes[0].set_title('Detecção de Anomalias (Escala Logarítmica)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Qtd. Lançamentos (log)')
axes[0].set_ylabel('Volume Líquido R$ (log)')
axes[0].legend(title='Status', labels=['Normal (1)', 'Anomalia (-1)'])

# Barras por Porte
porte_counts = anomalias['porte'].value_counts()
sns.barplot(
    x=porte_counts.values, 
    y=porte_counts.index, 
    hue=porte_counts.index, 
    palette='Reds_r', 
    legend=False, 
    ax=axes[1]
)
axes[1].set_title('Anomalias Detectadas por Porte', fontsize=12, fontweight='bold')
axes[1].set_xlabel('Quantidade de Alertas')
axes[1].set_ylabel('Porte')

# Histograma do Score
sns.histplot(data=df_test, x='score_anomalia', hue='target_anomalia', palette={1: '#3498db', -1: '#e74c3c'}, bins=30, kde=True, ax=axes[2])
axes[2].axvline(x=0, color='black', linestyle='--', alpha=0.7, label='Limiar de Decisão')
axes[2].set_title('Distribuição do Score de Anomalia', fontsize=12, fontweight='bold')
axes[2].set_xlabel('Score de Anomalia (Mais negativo = Mais atípico)')
axes[2].set_ylabel('Frequência')

plt.tight_layout()
plt.show()

# 9. TOP OUTLIERS E PROPORÇÃO DE RISCO
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

top10_anomalias = anomalias.head(10).copy()
top10_anomalias['conta_label'] = [f"ID {idx} ({porte})" for idx, porte in zip(top10_anomalias.index, top10_anomalias['porte'])]
top10_anomalias['vllanliq_bi'] = top10_anomalias['vllanliq'] / 1e9

sns.barplot(
    data=top10_anomalias, x='vllanliq_bi', y='conta_label', hue='porte',
    dodge=False, palette='Set2', ax=axes[0]
)
axes[0].set_title('Top 10 Anomalias (Por Severidade do Score)', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Volume Líquido (em Bilhões de R$)')
axes[0].set_ylabel('Conta / ID Original (Porte)')
axes[0].legend(title='Porte Empresarial')

# Donut Chart
qtd_pequenos = len(pequenos_suspeitos)
qtd_outros = len(anomalias) - qtd_pequenos
labels = ['Alto Risco\n(PF / Microempresa)', 'Outros Portes\n(Demais / Não Informado)']
valores = [qtd_pequenos, qtd_outros]

axes[1].pie(
    valores, labels=labels, autopct='%1.1f%%', startangle=140, 
    colors=['#e74c3c', '#34495e'], wedgeprops=dict(width=0.4, edgecolor='w')
)
axes[1].set_title(f'Composição das {len(anomalias)} Anomalias Detectadas', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()