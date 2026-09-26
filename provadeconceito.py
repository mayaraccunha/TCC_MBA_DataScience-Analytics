import pandas as pd
import json
import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# 1. CARREGAR A BASE DO BRASIL (AGROFIT)
# Usamos sep=';' e econding='utf-8' para ler os dados do governo corretamente
df_br = pd.read_csv('agrofitprodutostecnicos.csv', sep=';', encoding='utf-8')

# Função Regex para limpar o texto: pega apenas o que está antes do primeiro parêntesis
def limpar_ingrediente(texto):
    if pd.isna(texto): return ""
    match = re.match(r"([^\(]+)", texto)
    if match:
        return match.group(1).strip().upper()
    return str(texto).strip().upper()

# Cria a coluna limpa
df_br['ingrediente_limpo'] = df_br['INGREDIENTE_ATIVO(GRUPO_QUIMICI)(CONCENTRACAO)'].apply(limpar_ingrediente)

# 2. CARREGAR A BASE DA UNIÃO EUROPEIA (JSON)
# O ficheiro europeu tem um objeto JSON por linha
with open('PIMS_PIMS_TR_ACTIVE_SUBSTANCES_PUBLIC.json', 'r', encoding='utf-8') as f:
    eu_data = [json.loads(line) for line in f]
    
df_eu = pd.DataFrame(eu_data)

# Padronizar o nome do ingrediente na Europa para letras maiúsculas para o cruzamento bater certo
df_eu['ingrediente_limpo'] = df_eu['substance_name'].str.strip().str.upper()

# 3. O CRUZAMENTO INVESTIGATIVO (O DUPLO PADRÃO)
# Juntamos as bases onde os ingredientes limpos são iguais
df_cruzamento = pd.merge(df_br, df_eu, on='ingrediente_limpo', how='inner')

# Filtramos: Aprovado no Brasil mais Banido ("Not approved") na Europa!
duplo_padrao = df_cruzamento[df_cruzamento['substance_status'] == 'Not approved']

# Mostra as primeiras descobertas
colunas_resultado = ['PRODUTO_TECNICO_MARCA_COMERCIAL', 'ingrediente_limpo', 'substance_status', 'classification_reg_1272']
print("Descobertas do Cruzamento (Veneno Banido na UE, mas vendido no BR):")
print(duplo_padrao[colunas_resultado].head())

# 4. AVALIAÇÃO DSE IMPACTO (PRODUTOS FORMULADOS)
# Carrega a base do produto final que vai para a lavoura.
# Substitua o nome do arquivo se o seu CSV estiver com nome diferente.
try:
    df_form = pd.read_csv('agrofitprodutosformulados.csv', sep=';', encoding='utf-8')
except FileNotFoundError:
    print("Por favor, garanta que o arquivo 'agrofitprodutosformulados.csv está na pasta datasets")
    exit()


    
# Aplica a mesma função Regex para criar a chave de relacionamento perfeita
df_form['ingrediente_limpo'] = df_form['INGREDIENTE_ATIVO'].apply(limpar_ingrediente)

# Faz o merge cruzando a Tabela Fato (Formulados) com a lista de "Duplo Padrão"
# Tiramos aa duplicatas do duplo_padrao para evitar duplicatas de linhas no merge
dimensao_banidos = duplo_padrao[['ingrediente_limpo', 'substance_status', 'classification_reg_1272']].drop_duplicates()
df_impacto_real = pd.merge(df_form, dimensao_banidos, on='ingrediente_limpo', how='inner')

# Agrupa os dados para ver o volume do problema:
# Quantos produtos comerciais diferentes carregam cada ingrediente banido?
resumo_mercado = df_impacto_real.groupby('ingrediente_limpo').size().reset_index(name='qtd_produtos_comerciais')
resumo_mercado = resumo_mercado.sort_values(by='qtd_produtos_comerciais', ascending=False)

print("\n--- Volume do Colonialismo Químico ---")
print("Top 5 Ingredientes banidos na UE com mais produtos comerciais no Brasil:")
print(resumo_mercado.head())

print("\n--- Iniciando Processamento de Linguagem natural (NLP) e Machine Learning ---")

# 5. ENGENHARIA DE FEATURES (MINERAÇÃO DE TEXTO NO LAUDO EUROPEU)
# Vamos extrair do texto as classificações de perigo usando Regex e criar colunas binárias (0 ou 1)
def extrair_riscos(texto):
    texto = str(texto).upper()
    return pd.Series({
        'risco_aquatico': 1 if 'AQUATIC' in texto else 0,
        'risco_agudo_humano': 1 if 'ACUTE TOX' in texto else 0,
        'risco_cancer_mutacao': 1 if 'CARC' in texto or 'MUTA' in texto else 0,
        'risco_reprodutivo': 1 if 'REPR' in texto else 0
    })
    
# Aplica a função da tabela resumo que criamos no passo anterior
# (Precisa garantir que a coluna classification_reg_1272 esteja no resumo_mercado)
resumo_mercado = df_impacto_real.groupby(
    ['ingrediente_limpo', 'classification_reg_1272'], dropna=False
).size().reset_index(name='qtd_produtos_comerciais')

# Expandi os laudos textuais em colunas matemáticas
features_risco = resumo_mercado['classification_reg_1272'].apply(extrair_riscos)
df_ml = pd.concat([resumo_mercado, features_risco], axis=1)

# Lidando com valores nulos caso a Europa não tenha fornecido o laudo exato
df_ml.fillna(0, inplace=True)

# 6. MACHINE LEARNING: ALGORITMO K-MEANS (CLUSTERIZAÇÃO)
# Seleciona as variáveis que o algoritmo vai usar para aprender
variaveis_modelo = ['qtd_produtos_comerciais', 'risco_aquatico', 'risco_agudo_humano', 'risco_cancer_mutacao', 'risco_reprodutivo']
X = df_ml[variaveis_modelo]

# Padronização (Standard Scaler): O K-Means é sensível a escalas
# Precisa nivelar o "volume comercial" com as marcações de risco (que são 0 e 1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Treinamento do Modelo (vamos forçar 3 grupos: Risco Moderado, Risco Alto, Risco Crítico)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df_ml['cluster_risco'] = kmeans.fit_predict(X_scaled)

# Ordenando para ver os piores casos primeiro (Alto volume de vendas + Alto Risco)
df_ml = df_ml.sort_values(by=['cluster_risco', 'qtd_produtos_comerciais'], ascending=[False, False])

print("\nAlgoritmo Treinado com Sucesso! Amostra dos Clusters gerados:")
print(df_ml[['ingrediente_limpo', 'qtd_produtos_comerciais', 'risco_cancer_mutacao', 'risco_aquatico', 'cluster_risco']].head(10))

# EXPORTAÇÃOPARA A ÁREA DE STAGING
df_form.to_csv('stage_df_form.csv', sep=';', index=False, encoding='utf-8')
df_ml.to_csv('stage_df_ml.csv', sep=';', index=False, encoding='utf-8')

print("Fase de Processamento e ML concluída, Dados guardados na área de staging para carga no MySQL.")