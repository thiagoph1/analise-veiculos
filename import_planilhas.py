import pandas as pd
import pymongo
import os
from glob import glob

# Conectar ao MongoDB Atlas
mongo_uri = "mongodb+srv://dbVeiculos:a315saex@veiculoscluster.2fyqhfr.mongodb.net/?retryWrites=true&w=majority&appName=VeiculosCluster"
client = pymongo.MongoClient(mongo_uri)
db = client['veiculos_db']

# Pasta com planilhas
planilhas_dir = "caminho/para/suas/planilhas"  # Ex.: "C:/Users/SeuUsuario/planilhas"

# Listar planilhas .xlsx
planilhas = glob(os.path.join(planilhas_dir, "*.xlsx"))

for planilha_path in planilhas:
    # Extrair data do nome do arquivo (ex.: 2025-05-12.xlsx)
    filename = os.path.basename(planilha_path)
    date = filename.replace('.xlsx', '').replace('-', '_')
    collection_name = f'veiculos_{date}'
    collection = db[collection_name]
    
    # Verificar se a coleção já existe
    if collection.count_documents({}) > 0:
        print(f"Coleção {collection_name} já existe, pulando...")
        continue
    
    try:
        # Ler planilha
        data = pd.read_excel(planilha_path, engine='openpyxl')
        
        # Verificar colunas obrigatórias
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            print(f"Colunas ausentes em {filename}: {[col for col in required_columns if col not in data.columns]}")
            continue
        
        # Converter para documentos
        documents = data.to_dict('records')
        if documents:
            collection.insert_many(documents)
            print(f"{len(documents)} documentos inseridos em {collection_name}")
    except Exception as e:
        print(f"Erro ao processar {filename}: {str(e)}")

client.close()