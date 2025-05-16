import pandas as pd
import pymongo
import os
import glob
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Conectar ao MongoDB Atlas
mongo_uri = os.environ.get('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI não configurado")
client = pymongo.MongoClient(mongo_uri)
db = client['veiculos_db']

# Pasta com planilhas
planilhas_dir = "uploads"

# Listar planilhas .xlsx
planilhas = glob.glob(os.path.join(planilhas_dir, "*.xlsx"))

for planilha_path in planilhas:
    # Extrair data do nome do arquivo (ex.: 2025-05-16.xlsx)
    filename = os.path.basename(planilha_path)
    if not filename.endswith('.xlsx') or not filename.replace('.xlsx', '').replace('-', '').isdigit():
        logging.warning(f"Nome de arquivo inválido, pulando: {filename}")
        continue
    
    date = filename.replace('.xlsx', '').replace('-', '_')
    collection_name = f'veiculos_{date}'
    collection = db[collection_name]
    
    # Verificar se a coleção já existe
    if collection.count_documents({}) > 0:
        logging.info(f"Coleção {collection_name} já existe, pulando...")
        continue
    
    try:
        # Ler planilha
        data = pd.read_excel(planilha_path, engine='openpyxl')
        
        # Verificar colunas obrigatórias
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            logging.error(f"Colunas ausentes em {filename}: {[col for col in required_columns if col not in data.columns]}")
            continue
        
        # Converter para documentos
        documents = data.to_dict('records')
        if documents:
            collection.insert_many(documents)
            logging.info(f"{len(documents)} documentos inseridos em {collection_name}")
    except Exception as e:
        logging.error(f"Erro ao processar {filename}: {str(e)}")

client.close()