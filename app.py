from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pymongo
import os
import bcrypt

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta')  # Fallback para local
CORS(app, resources={r"/*": {"origins": ["https://seu-dominio-render.com", "http://localhost:8000"]}})  # Atualize com o domínio do Render

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'

# Conectar ao MongoDB Atlas
mongo_uri = os.environ.get('MONGO_URI')
if not mongo_uri:
    raise ValueError("MONGO_URI não configurado nas variáveis de ambiente")
client = pymongo.MongoClient(mongo_uri)
db = client['veiculos_db']

# Modelo de usuário
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Lista de unidades "Elos do SISTRAN"
ELOS_SISTRAN = [
    'AFA', 'BAAN', 'BABV', 'BACG', 'BAFL', 'BAFZ', 'BANT', 'BAPV', 'BASC', 'BASM', 'BASV',
    'CISCEA', 'CLA', 'COMARA', 'CPBV-CC', 'CRCEA-SE', 'DACTA I', 'DACTA II', 'DACTA III',
    'DACTA IV', 'DECEA', 'EEAR', 'EPCAR', 'GABAER', 'GAP-AF', 'GAP-BE', 'GAP-BR', 'GAP-CO',
    'GAP-DF', 'GAP-GL', 'GAP-LS', 'GAP-MN', 'GAP-RF', 'GAP-RJ', 'GAP-SJ', 'GAP-SP', 'ICEA', 'PAME', 'CABE', 'CABW'
]

@login_manager.user_loader
def load_user(user_id):
    user = db.users.find_one({'username': user_id})
    return User(user_id) if user else None

# Função para verificar credenciais
def verify_password(username, password):
    user = db.users.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
        return True
    return False

# Função para registrar os Blueprints (assumindo que login_bp usa verify_password)
def register_blueprints():
    from routes.login import login_bp
    from routes.logout import logout_bp
    from routes.index import index_bp
    from routes.upload import upload_bp
    from routes.dates import dates_bp
    from routes.tdvs import tdvs_bp
    from routes.report import report_bp
    from routes.tdv_report import tdv_report_bp
    from routes.tdv_unidade_report import tdv_unidade_report_bp
    from routes.status_patrimonio_chart import status_patrimonio_chart_bp
    from routes.disponibilidade_chart import disponibilidade_chart_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(dates_bp)
    app.register_blueprint(tdvs_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(tdv_report_bp)
    app.register_blueprint(tdv_unidade_report_bp)
    app.register_blueprint(status_patrimonio_chart_bp)
    app.register_blueprint(disponibilidade_chart_bp)

# Registrar os Blueprints após a inicialização do app
register_blueprints()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)