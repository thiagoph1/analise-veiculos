from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pymongo
import os

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

# Conectar ao MongoDB Atlas
mongo_uri = os.environ.get('MONGO_URI')
client = pymongo.MongoClient(mongo_uri)
db = client['veiculos_db']

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
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
        
        # Extrair data do nome do arquivo (assumindo formato YYYY-MM-DD.xlsx)
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
def get_dates():
    collections = db.list_collection_names()
    dates = [col.replace('veiculos_', '').replace('_', '-') for col in collections if col.startswith('veiculos_')]
    dates.sort(reverse=True)
    return jsonify({'dates': dates})

@app.route('/report/<date>', methods=['GET'])
def get_report(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        # Carregar dados
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        
        # Gerar relatório
        report = data.groupby('Marca').size().to_dict()
        chart_data = {
            'labels': data.groupby('Ano modelo').size().index.astype(str).tolist(),
            'values': data.groupby('Ano modelo').size().values.tolist()
        }
        
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chart/<date>/status_patrimonio', methods=['GET'])
def get_status_patrimonio_chart(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        # Carregar dados
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        
        # Verificar coluna Status Patrimonio
        if 'Status Patrimonio' not in data.columns:
            return jsonify({'error': 'Coluna Status Patrimonio não encontrada'}), 400
        
        # Gerar dados do gráfico
        chart_data = {
            'labels': data.groupby('Status Patrimonio').size().index.tolist(),
            'values': data.groupby('Status Patrimonio').size().values.tolist()
        }
        
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))