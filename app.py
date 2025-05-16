from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import pymongo
import logging
import os
from datetime import datetime
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configura logging para depuração
logging.basicConfig(level=logging.DEBUG)

# Conectar ao MongoDB Atlas
mongo_uri = os.environ.get('MONGO_URI', 'mongodb+srv://dbVeiculos:a315saex@veiculoscluster.2fyqhfr.mongodb.net/?retryWrites=true&w=majority&appName=VeiculosCluster')
client = pymongo.MongoClient(mongo_uri)
db = client['veiculos_db']

@app.route('/')
def serve_index():
    app.logger.debug("Acessando rota /")
    return send_from_directory('public', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.debug("Recebida requisição para /upload")
    
    if 'file' not in request.files:
        app.logger.error("Nenhum arquivo enviado")
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename is None or file.filename == '':
        app.logger.error("Nenhum arquivo selecionado")
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if not file.filename.endswith('.xlsx'):
        app.logger.error("Arquivo não é .xlsx")
        return jsonify({'error': 'Arquivo deve ser .xlsx'}), 400
    
    try:
        # Definir coleção para o dia atual
        today = datetime.now().strftime('%Y_%m_%d')
        collection_name = f'veiculos_{today}'
        collection = db[collection_name]
        
        # Verificar se já existe uma planilha para hoje
        if collection.count_documents({}) > 0:
            app.logger.error("Planilha já existe para hoje")
            return jsonify({'error': 'Planilha já existe para hoje'}), 400
        
        # Processar planilha
        file_data = file.read()
        data = pd.read_excel(BytesIO(file_data), engine='openpyxl')
        
        app.logger.debug("Verificando colunas")
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in data.columns]
            app.logger.error(f"Colunas ausentes: {missing}")
            return jsonify({'error': f"Colunas ausentes: {missing}"}), 400
        
        # Converter planilha para documentos MongoDB
        documents = data.to_dict('records')
        if documents:
            collection.insert_many(documents)
            app.logger.debug(f"{len(documents)} documentos inseridos em {collection_name}")
        
        # Gerar relatório: contagem de veículos por Marca
        report = data.groupby('Marca').size().to_dict()
        
        # Gerar dados do gráfico: contagem de veículos por Ano modelo
        chart_data = {
            'labels': data['Ano modelo'].value_counts().index.tolist(),
            'values': data['Ano modelo'].value_counts().values.tolist()
        }
        
        app.logger.debug("Retornando relatório e dados do gráfico")
        return jsonify({
            'report': report,
            'chart': chart_data
        })
    except Exception as e:
        app.logger.error(f"Erro ao processar arquivo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/dates', methods=['GET'])
def get_dates():
    app.logger.debug("Recebida requisição para /dates")
    try:
        # Listar coleções que começam com 'veiculos_'
        collections = db.list_collection_names()
        dates = [col.replace('veiculos_', '').replace('_', '-') for col in collections if col.startswith('veiculos_')]
        dates.sort(reverse=True)
        app.logger.debug(f"Datas disponíveis: {dates}")
        return jsonify({'dates': dates})
    except Exception as e:
        app.logger.error(f"Erro ao listar datas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/report/<date>', methods=['GET'])
def get_report(date):
    app.logger.debug(f"Recebida requisição para /report/{date}")
    
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    try:
        # Buscar todos os documentos da coleção
        documents = list(collection.find({}))
        if not documents:
            app.logger.error(f"Planilha não encontrada para {date}")
            return jsonify({'error': f"Planilha não encontrada para {date}"}), 404
        
        # Converter para DataFrame
        data = pd.DataFrame(documents)
        
        app.logger.debug("Verificando colunas")
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            missing = [col for col in required_columns if col not in data.columns]
            app.logger.error(f"Colunas ausentes: {missing}")
            return jsonify({'error': f"Colunas ausentes: {missing}"}), 400
        
        # Gerar relatório: contagem de veículos por Marca
        report = data.groupby('Marca').size().to_dict()
        
        # Gerar dados do gráfico: contagem de veículos por Ano modelo
        chart_data = {
            'labels': data['Ano modelo'].value_counts().index.tolist(),
            'values': data['Ano modelo'].value_counts().values.tolist()
        }
        
        app.logger.debug("Retornando relatório e dados do gráfico")
        return jsonify({
            'report': report,
            'chart': chart_data
        })
    except Exception as e:
        app.logger.error(f"Erro ao processar relatório: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)