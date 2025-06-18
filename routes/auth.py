from flask_login import UserMixin  # type: ignore
import pymongo  # type: ignore
from bson.binary import Binary  # type: ignore
import bcrypt  # type: ignore
import os

# Conectar ao MongoDB (usando a URI do ambiente)
mongo_uri = os.environ.get('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI não configurado nas variáveis de ambiente")
client = pymongo.MongoClient(mongo_uri)

# Definir conexões para os bancos
usuarios_db = client['usuarios']
veiculos_db = client['veiculos_db']
idealTDV_db = client['idealTDV']

# Função para acessar os bancos de dados
def get_db(db_name):
    if db_name == 'usuarios':
        return usuarios_db
    elif db_name == 'veiculos_db':
        return veiculos_db
    elif db_name == 'idealTDV':
        return idealTDV_db
    else:
        raise ValueError(f"Banco de dados '{db_name}' não suportado")

# Modelo de usuário
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Função para verificar credenciais
def verify_password(username, password):
    user = usuarios_db.users.find_one({'username': username})
    if user:
        password_hash = user['password_hash']
        if isinstance(password_hash, Binary):
            password_hash = password_hash.to_python()  # Converter Binary para bytes
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            return True
    return False

# Função para carregar usuário (para Flask-Login)
def load_user(user_id):
    try:
        user = usuarios_db.users.find_one({'username': user_id})
        if user:
            return User(user_id)
        else:
            return None
    except Exception as e:
        return None