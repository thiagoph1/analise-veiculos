import pymongo
import os

mongo_uri = os.environ.get('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI não configurado nas variáveis de ambiente")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client['usuarios']
    # Testar a conexão pingando o servidor
    client.admin.command('ping')
    print("Conexão com o MongoDB bem-sucedida!")
except Exception as e:
    print(f"Erro de conexão: {e}")