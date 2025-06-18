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
db = client['idealTDV']

# Pasta com planilhas
planilhas_dir = "TDV"

# Coleção para quantidades ideais
ideal_collection = db['idealTDV']

# Listar planilhas .xlsx
planilhas = glob.glob(os.path.join(planilhas_dir, "*.xlsx"))

for planilha_path in planilhas:
    # Extrair nome do arquivo
    filename = os.path.basename(planilha_path)
    if not filename.endswith('.xlsx'):
        logging.warning(f"Arquivo inválido, pulando: {filename}")
        continue

    try:
        # Ler planilha específica 'Planilha1'
        data = pd.read_excel(planilha_path, engine='openpyxl', sheet_name='Planilha1')
        
        # Verificar se a primeira coluna é "OM"
        if data.columns[0] != 'OM':
            logging.error(f"Coluna 'OM' ausente em {filename}")
            continue
        
        # Obter os tipos de TDV (colunas P-0 a E-28)
        tdv_columns = data.columns[1:].tolist()  # Exclui "OM"
        
        # Transformar os dados
        ideal_data = []
        for index, row in data.iterrows():
            unidade = row['OM']
            for tdv in tdv_columns:
                quantidade = int(row[tdv]) if pd.notna(row[tdv]) and row[tdv] > 0 else 0
                if quantidade > 0:
                    ideal_data.append({
                        'Unidade': unidade,
                        'Tdv': tdv,
                        'Quantidade': quantidade
                    })
        
        # Verificar se há dados
        if not ideal_data:
            logging.warning(f"Nenhum dado válido encontrado em {filename}")
            continue
        
        # Inserir no MongoDB
        result = ideal_collection.insert_many(ideal_data)
        logging.info(f"{len(ideal_data)} quantidades ideais inseridas de {filename}")
        
    except Exception as e:
        logging.error(f"Erro ao processar {filename}: {str(e)}")

client.close()