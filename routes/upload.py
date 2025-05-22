from flask import Blueprint, request, jsonify
from flask_login import login_required
import pandas as pd

# Definir o Blueprint
upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    from app import db  # Importar dentro da função

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