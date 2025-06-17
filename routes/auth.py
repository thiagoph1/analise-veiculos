from flask_login import UserMixin
import pymongo
from bson.binary import Binary  # Importar de bson.binary
import bcrypt
import os

# Conectar ao MongoDB (usando a URI do ambiente)
mongo_uri = os.environ.get('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI não configurado nas variáveis de ambiente")
client = pymongo.MongoClient(mongo_uri)
db = client['usuarios']  # Usando o banco 'usuarios'

# Modelo de usuário
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Função para verificar credenciais com depuração
def verify_password(username, password):
    user = db.users.find_one({'username': username})
    if user:
        password_hash = user['password_hash']
        print(f"Hash encontrado para {username}: {password_hash}")  # Depuração
        if isinstance(password_hash, Binary):  # Usar bson.binary.Binary
            password_hash = password_hash.to_python()  # Converter Binary para bytes
            print(f"Hash convertido: {password_hash}")  # Depuração
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            return True
    return False

# Função para carregar usuário (para Flask-Login) com depuração
def load_user(user_id):
    print(f"Carregando usuário com ID: {user_id}")  # Depuração
    try:
        user = db.users.find_one({'username': user_id})
        if user:
            print(f"Usuário encontrado: {user}")  # Depuração
            return User(user_id)
        else:
            print(f"Usuário não encontrado para ID: {user_id}")  # Depuração
            return None
    except Exception as e:
        print(f"Erro ao carregar usuário: {e}")  # Depuração
        return None