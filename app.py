from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager # type: ignore
import os
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__, static_folder='public', static_url_path='')
app.template_folder = 'public/templates'  # Define explicitamente o diretório de templates
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta')  # Fallback para local
CORS(app, resources={r"/*": {"origins": ["https://seu-dominio-render.com", "http://localhost:8000"]}})  # Atualize com o domínio do Render

#Juntar as adidâncias
ADIDANCIAS = ['AD-CHINA', 'ADIAE-AFS', 'ADIAE-ARG', 'ADIAE-CHI', 'ADIAE-COL', 'ADIAE-CZE', 'ADIAE-FRA', 'ADIAE-ING', 'ADIAE-PAR', 'ADIAE-PER', 'ADIAE-URU', 'AD-INDIA', 'AD-INDONE', 'AD-SUECIA']

# Definir constante ELOS_SISTRAN (ajuste com todas as unidades reais)
ELOS_SISTRAN = ['AFA', 'BAAN', 'BABV', 'BACG', 'BAFL', 'BAFZ', 'BANT', 'BAPV', 'BASC', 'BASM', 'BASV', 'CISCEA', 'CLA', 'COMARA', 'CPBV-CC', 'CRCEA-SE', 'DACTA I', 'DACTA II', 'DACTA III', 'DACTA IV', 'DECEA', 'EEAR', 'EPCAR', 'GABAER', 'GAP-AF', 'GAP-BE', 'GAP-BR', 'GAP-CO', 'GAP-DF', 'GAP-GL', 'GAP-LS', 'GAP-MN', 'GAP-RF', 'GAP-RJ', 'GAP-SJ', 'GAP-SP', 'ICEA', 'PAME']

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'

# Importar funções de autenticação de auth.py
from routes.auth import load_user, verify_password  # Importação de funções específicas

# Configurar o user_loader do Flask-Login
login_manager.user_loader(load_user)

# Registro dos Blueprints
def register_blueprints():
    from routes.login import login_bp
    from routes.logout import logout_bp
    from routes.index import index_bp
    from routes.reports import reports_bp  # Novo Blueprint unificado
    from routes.charts import charts_bp  # Adicionar importação do charts_bp

    app.register_blueprint(login_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(reports_bp)  # Registrar o novo Blueprint
    app.register_blueprint(charts_bp)  # Registrar o charts_bp

# Registrar os Blueprints após a inicialização
register_blueprints()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)