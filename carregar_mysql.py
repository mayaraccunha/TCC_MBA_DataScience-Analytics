import pandas as pd
from sqlalchemy import create_engine

print("--- Iniciando Carregamento no Banco de Dados MySQL ---")

# 1. Leitura dos dados processados (Staging)
try:
    df_form = pd.read_csv('stage_df_form.csv', sep=';', encoding='utf-8')
    df_ml = pd.read_csv('stage_df_ml.csv', sep=';', encoding='utf-8')
except FileNotFoundError:
    print("Erro: Arquivos de staging não encontrados. Execute o script de processamento primeiro.")
    exit()
    
# 2. Conexão com o MysSQL
engine = create_engine('mysql+pymysql://root:SENHA_AQUI@localhost:3306/colonialismo_quimico')

# 3. Populando a Tabela dim_ingrediente
print("Limpando a lista de ingredientes...")
df_dim_ing = pd.DataFrame({'nome_ingrediente': df_form['ingrediente_limpo'].unique()})
df_dim_ing = df_dim_ing[df_dim_ing['nome_ingrediente'].notna()] 

print("Inserindo dados na dim_ingrediente...")
try:
    df_dim_ing.to_sql('dim_ingrediente', con=engine, if_exists='append', index=False)
    print("Ingredientes inseridos com sucesso.")
except Exception as e:
    print("Os ingredientes já existem no banco. Pulando a inserção para evitar duplicatas.")

# Resgatar os IDs gerados pelo MySQL para garantir a integridade relacional
print("Resgatando os IDs criados pelo banco...")
dim_ing_db = pd.read_sql("SELECT id_ingrediente, nome_ingrediente FROM dim_ingrediente", con=engine)
print(f"Total de ingredientes resgatados: {len(dim_ing_db)}")

# 4. Preparando e populando a dim_regulacao_ue
print("Preparando a tabela de regulação europeia...")
df_reg = df_ml.merge(dim_ing_db, left_on='ingrediente_limpo', right_on='nome_ingrediente', how='inner')

# Recriamos a coluna de status manualmente para o banco de dados
df_reg['substance_status'] = 'Not approved'

df_reg_final = df_reg[['id_ingrediente', 'substance_status', 'classification_reg_1272', 
                       'risco_aquatico', 'risco_agudo_humano', 'risco_cancer_mutacao', 
                       'risco_reprodutivo', 'cluster_risco']].copy()

df_reg_final.columns = ['id_ingrediente', 'status_aprovacao_ue', 'classificacao_original_1272', 
                        'risco_aquatico', 'risco_agudo_humano', 'risco_cancer_mutacao', 
                        'risco_reprodutivo', 'cluster_ia']

try:
    df_reg_final.to_sql('dim_regulacao_ue', con=engine, if_exists='append', index=False)
    print("Tabela dim_regulacao_ue populada com sucesso!")
except Exception as e:
    print("Erro ao inserir na dim_regulacao_ue:", e)
    
# 5. Preparando e populando a fato_produto_formulado
df_fato = df_form.merge(dim_ing_db, left_on='ingrediente_limpo', right_on='nome_ingrediente', how='inner')

df_fato_final = df_fato[['NR_REGISTRO', 'id_ingrediente', 'MARCA_COMERCIAL', 'TITULAR_DE_REGISTRO',
                         'CLASSE', 'CLASSE_TOXICOLOGICA', 'CLASSE_AMBIENTAL']].copy()

df_fato_final.columns = ['nr_registro', 'id_ingrediente', 'marca_comercial', 'titular_registro',
                         'classe_uso', 'classe_toxicologica_br', 'classe_ambiental_br']

df_fato_final = df_fato_final.drop_duplicates(subset=['nr_registro'])

try:
    df_fato_final.to_sql('fato_produto_formulado', con= engine, if_exists='append', index=False)
    print("Carga no MySQL concluída com sucesso! A arquitetura de dados está pronta para análise.")
except Exception as e:
    print("Erro ao inserir na fato_produto_formulado:", e)