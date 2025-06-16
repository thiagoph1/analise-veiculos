from flask_login import UserMixin
import pymongo
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

# Função para verificar credenciais
def verify_password(username, password):
    user = db.users.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return True
    return False

# Função para carregar usuário (para Flask-Login)
def load_user(user_id):
    user = db.users.find_one({'username': user_id})
    return User(user_id) if user else None