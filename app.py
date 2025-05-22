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

# Lista de unidades "Elos do SISTRAN"
ELOS_SISTRAN = [
    'AFA', 'BAAN', 'BABV', 'BACG', 'BAFL', 'BAFZ', 'BANT', 'BAPV', 'BASC', 'BASM', 'BASV',
    'CISCEA', 'CLA', 'COMARA', 'CPBV-CC', 'CRCEA-SE', 'DACTA I', 'DACTA II', 'DACTA III',
    'DACTA IV', 'DECEA', 'EEAR', 'EPCAR', 'GABAER', 'GAP-AF', 'GAP-BE', 'GAP-BR', 'GAP-CO',
    'GAP-DF', 'GAP-GL', 'GAP-LS', 'GAP-MN', 'GAP-RF', 'GAP-RJ', 'GAP-SJ', 'GAP-SP', 'ICEA', 'PAME'
]

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

@app.route('/tdvs/<date>', methods=['GET'])
@login_required
def get_tdvs(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0, 'Tdv': 1})))
        if 'Tdv' not in data.columns:
            return jsonify({'error': 'Coluna Tdv não encontrada'}), 400
        tdvs = sorted(data['Tdv'].dropna().unique().tolist())
        return jsonify({'tdvs': tdvs})
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
            return jsonify({'error': 'Coluna Tdv não encontrada'}), 400
        report = data.groupby('Tdv').size().to_dict()
        chart_data = {
            'labels': data.groupby('Tdv').size().index.tolist(),
            'values': data.groupby('Tdv').size().values.tolist()
        }
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/report/<date>/tdv_unidade', methods=['GET'])
@app.route('/report/<date>/tdv_unidade/<tdv>', methods=['GET'])
@login_required
def get_tdv_unidade_report(date, tdv=None):
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
        
        # Filtrar por TDV, se fornecido
        if tdv and tdv != 'all':
            data = data[data['Tdv'] == tdv]
            if data.empty:
                return jsonify({'report': []}), 200
        
        report = data.groupby(['Tdv', 'Unidade']).size().reset_index(name='Quantidade')
        report_data = report.to_dict('records')
        return jsonify({'report': report_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<date>/status_patrimonio', methods=['GET'])
@app.route('/chart/<date>/status_patrimonio/<unit_filter>', methods=['GET'])
@login_required
def get_status_patrimonio_chart(date, unit_filter=None):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        if 'Status Patrimonio' not in data.columns or 'Unidade' not in data.columns:
            missing = ['Status Patrimonio' if 'Status Patrimonio' not in data.columns else '', 'Unidade' if 'Unidade' not in data.columns else '']
            missing = [m for m in missing if m]
            return jsonify({'error': f'Colunas ausentes: {missing}'}), 400
        
        # Aplicar filtro de unidades
        if unit_filter == 'elos':
            data = data[data['Unidade'].isin(ELOS_SISTRAN)]
        elif unit_filter == 'extras':
            data = data[~data['Unidade'].isin(ELOS_SISTRAN)]
        
        if data.empty:
            return jsonify({'chart': {'labels': [], 'values': []}}), 200
        
        chart_data = {
            'labels': data.groupby('Status Patrimonio').size().index.tolist(),
            'values': [int(x) for x in data.groupby('Status Patrimonio').size().values.tolist()]  # Converter int64 para int
        }
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<date>/disponibilidade', methods=['GET'])
@app.route('/chart/<date>/disponibilidade/<unit_filter>', methods=['GET'])
@login_required
def get_disponibilidade_chart(date, unit_filter=None):
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
        
        # Aplicar filtro de unidades
        if unit_filter == 'elos':
            data = data[data['Unidade'].isin(ELOS_SISTRAN)]
        elif unit_filter == 'extras':
            data = data[~data['Unidade'].isin(ELOS_SISTRAN)]
        
        if data.empty:
            return jsonify({'chart': {'labels': [], 'datasets': [{'label': 'Disponível', 'data': []}, {'label': 'Indisponível', 'data': []}]}}), 200
        
        # Log para depuração
        print("Valores únicos em Unidade após filtro:", data['Unidade'].unique().tolist())
        
        # Definir categorias
        disponiveis = ['Em Uso', 'Em Trânsito', 'Estoque Interno']
        indisponiveis = ['A Alienar', 'Em Reparo', 'A Reparar', 'Inativo']
        
        # Criar coluna para categorizar status
        data['Categoria'] = data['Status Patrimonio'].apply(
            lambda x: 'Disponível' if x in disponiveis else 'Indisponível' if x in indisponiveis else 'Outros'
        )
        
        # Agrupar por Unidade e Categoria
        grouped = data.groupby(['Unidade', 'Categoria']).size().unstack(fill_value=0)
        
        # Garantir que Disponível e Indisponível existam
        if 'Disponível' not in grouped.columns:
            grouped['Disponível'] = 0
        if 'Indisponível' not in grouped.columns:
            grouped['Indisponível'] = 0
            
        # Log para depuração
        print("Dados agrupados:", grouped.to_dict())
        
        chart_data = {
            'labels': grouped.index.tolist(),
            'datasets': [
                {
                    'label': 'Disponível',
                    'data': [int(x) for x in grouped['Disponível'].tolist()],  # Converter int64 para int
                    'backgroundColor': 'rgba(34, 197, 94, 0.6)',
                    'borderColor': 'rgba(34, 197, 94, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Indisponível',
                    'data': [int(x) for x in grouped['Indisponível'].tolist()],  # Converter int64 para int
                    'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }
        return jsonify({'chart': chart_data})
    except Exception as e:
        print("Erro na rota /disponibilidade:", str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)