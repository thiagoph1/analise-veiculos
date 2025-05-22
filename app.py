from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import pandas as pd
import pymongo
import os
import bcrypt

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'sua_chave_secreta')  # Fallback para local
CORS(app, resources={r"/*": {"origins": ["https://seu-dominio-render.com", "http://localhost:8000"]}})  # Atualize com o domínio do Render

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

# Usuários com senhas hasheadas
users = {
    'admin': bcrypt.hashpw('a315saex'.encode('utf-8'), bcrypt.gensalt()),
    'sistran': bcrypt.hashpw('diradsistran'.encode('utf-8'), bcrypt.gensalt()),
    'user2': bcrypt.hashpw('senha789564'.encode('utf-8'), bcrypt.gensalt())
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id) if user_id in users else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error='Usuário e senha são obrigatórios'), 400
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Credenciais inválidas'), 401
    return render_template('login.html', error=None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if not file.filename or not file.filename.endswith('.xlsx'):
        return jsonify({'error': 'Arquivo deve ser .xlsx'}), 400
    
    try:
        # Ler planilha
        data = pd.read_excel(file, engine='openpyxl')
        
        # Verificar colunas obrigatórias
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in data.columns]
            return jsonify({'error': f'Colunas ausentes: {missing}'}), 400
        
        # Extrair data do nome do arquivo (formato YYYY-MM-DD.xlsx)
        date = file.filename.replace('.xlsx', '').replace('-', '_')
        collection_name = f'veiculos_{date}'
        collection = db[collection_name]
        
        # Verificar se a coleção já existe
        if collection.count_documents({}) > 0:
            return jsonify({'error': 'Dados para esta data já existem'}), 400
        
        # Inserir dados no MongoDB
        documents = data.to_dict('records')
        collection.insert_many(documents)
        
        # Gerar relatório
        report = data.groupby('Marca').size().to_dict()
        chart_data = {
            'labels': data.groupby('Ano modelo').size().index.astype(str).tolist(),
            'values': data.groupby('Ano modelo').size().values.tolist()
        }
        
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dates', methods=['GET'])
@login_required
def get_dates():
    try:
        collections = db.list_collection_names()
        dates = [col.replace('veiculos_', '').replace('_', '-') for col in collections if col.startswith('veiculos_')]
        dates.sort(reverse=True)
        return jsonify({'dates': dates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<date>', methods=['GET'])
@login_required
def get_report(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        report = data.groupby('Marca').size().to_dict()
        chart_data = {
            'labels': data.groupby('Ano modelo').size().index.astype(str).tolist(),
            'values': data.groupby('Ano modelo').size().values.tolist()
        }
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<date>/tdv', methods=['GET'])
@login_required
def get_tdv_report(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        if 'Tdv' not in data.columns:
            return jsonify({'error': 'Coluna TDV não encontrada'}), 400
        report = data.groupby('Tdv').size().to_dict()
        chart_data = {
            'labels': data.groupby('Tdv').size().index.tolist(),
            'values': data.groupby('Tdv').size().values.tolist()
        }
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<date>/tdv_unidade', methods=['GET'])
@login_required
def get_tdv_unidade_report(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        required_columns = ['Tdv', 'Unidade']
        if not all(col in data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in data.columns]
            return jsonify({'error': f'Colunas ausentes: {missing}'}), 400
        report = data.groupby(['Tdv', 'Unidade']).size().reset_index(name='Quantidade')
        report_data = report.to_dict('records')
        return jsonify({'report': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<date>/status_patrimonio', methods=['GET'])
@login_required
def get_status_patrimonio_chart(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        if 'Status Patrimonio' not in data.columns:
            return jsonify({'error': 'Coluna Status Patrimonio não encontrada'}), 400
        chart_data = {
            'labels': data.groupby('Status Patrimonio').size().index.tolist(),
            'values': data.groupby('Status Patrimonio').size().values.tolist()
        }
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<date>/disponibilidade', methods=['GET'])
@login_required
def get_disponibilidade_chart(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        if 'Unidade' not in data.columns or 'Status Patrimonio' not in data.columns:
            missing = ['Unidade' if 'Unidade' not in data.columns else '', 'Status Patrimonio' if 'Status Patrimonio' not in data.columns else '']
            missing = [m for m in missing if m]
            return jsonify({'error': f'Colunas ausentes: {missing}'}), 400
        disponiveis = ['Em Uso', 'Em Trânsito', 'Estoque Interno']
        indisponiveis = ['A Alienar', 'Em Reparo', 'A Reparar', 'Inativo']
        grouped = data.groupby(['Unidade', 'Status Patrimonio']).size().unstack(fill_value=0)
        chart_data = {
            'labels': grouped.index.tolist(),
            'datasets': [
                {
                    'label': 'Disponível',
                    'data': [grouped[status].sum() if status in grouped.columns else 0 for status in disponiveis],
                    'backgroundColor': 'rgba(37, 99, 235, 0.2)',
                    'borderColor': 'rgba(37, 99, 235, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Indisponível',
                    'data': [grouped[status].sum() if status in grouped.columns else 0 for status in indisponiveis],
                    'backgroundColor': 'rgba(255, 165, 0, 0.2)',
                    'borderColor': 'rgba(255, 165, 0, 1)',
                    'borderWidth': 1
                }
            ]
        }
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)