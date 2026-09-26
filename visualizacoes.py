import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

print("Carregando os dados exportados do MySQL...")
df_top10 = pd.read_csv('TOP10_ingredientes_banidos_UE.csv')
df_clusters = pd.read_csv('validacao_ml_cluster_kmeans.csv')

# Configurações do estilo visual
sns.set_theme(style="whitegrid")

# ====================================================================================================================================
# GRÁFICO 1: O COLONIALISMO QUIMÍCO EM FOCO (TOP 10)
#=====================================================================================================================================
plt.figure(figsize=(10,6))
ax1 = sns.barplot(x='total_produtos_comerciais_br', y='nome_ingrediente', 
                  data=df_top10, palette='Reds_r', hue='nome_ingrediente', legend=False)

plt.title('Top 10 Ingredientes Banidos na UE com Maior Presença no Brasil', fontsize=14, pad=15)
plt.xlabel('Total de Produtos Comerciais Registrados', fontsize=12)
plt.ylabel('Ingrediente Ativo', fontsize=12)

# Adiciona os rótulos de dados no final de cada barra
for p in ax1.patches:
    ax1.annotate(f"{int(p.get_width())}",
                 (p.get_width(), p.get_y() + p.get_height() / 2.),
                 ha='left', va='center', xytext=(5, 0), textcoords='offset points')
    
plt.tight_layout()
plt.savefig('grafico_top10.png', dpi=300) # Salva em alta resolução (300 dpi)
print("Gráfico 'grafico_top10.png' salvo com sucesso!")
plt.show()

# ====================================================================================================================================
# GRÁFICO 2: VALIDAÇÃO DO ALGORITMO K-MEANS
# ====================================================================================================================================
plt.figure(figsize=(8, 5))
ax2 = sns.barplot(x='cluster_risco', y='volume_total_produtos', 
                  data=df_clusters, palette='viridis', hue='cluster_risco', legend=False)

plt.title('Volume de Produtos por Cluster de Risco (k-Means)', fontsize=14, pad=15)
plt.xlabel('Cluster (Nível de Risco)', fontsize=12)
plt.ylabel('Volume Total de Produtos', fontsize=12)

# Adiciona os rotúlos de dados em cima de cada barra
for p in ax2.patches:
    ax2.annotate(f"{int(p.get_height())}", 
                 (p.get_x() + p.get_width() / 2., p.get_height()), 
                 ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')
    
plt.tight_layout()
plt.savefig('grafico_clusters.png', dpi=300) # Salva em alta resolução
print("Gráfico 'grafico_clusters.png' salvo com sucesso!")
plt.show()