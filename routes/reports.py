from flask import Blueprint, jsonify
from flask_login import login_required  # type: ignore
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso
import logging
logging.basicConfig(level=logging.INFO)

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/report/<date>', methods=['GET'])
@login_required
def get_report(date):
    from app import ELOS_SISTRAN  # Importar dentro da função para evitar ciclo

    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
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

@reports_bp.route('/report/<date>/tdv', methods=['GET'])
@login_required
def get_tdv_report(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
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

@reports_bp.route('/report/<date>/tdv_unidade', methods=['GET'])
@reports_bp.route('/report/<date>/tdv_unidade/<tdv>', methods=['GET'])
@login_required
def get_tdv_unidade_report(date, tdv=None):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    ideal_collection = get_db('idealTDV')['ideal_quantities']
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        # Carregar dados reais
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
        
        # Agrupar dados reais
        report = data.groupby(['Tdv', 'Unidade']).size().reset_index(name='Quantidade')
        real_data = report.to_dict('records')

        # Carregar dados ideais do MongoDB
        ideal_data = pd.DataFrame(list(ideal_collection.find({}, {'_id': 0})))
        if ideal_data.empty:
            logging.warning('Nenhum dado ideal encontrado na coleção ideal_quantities')
            ideal_dict = {}
        else:
            ideal_dict = ideal_data.set_index(['Unidade', 'Tdv'])['QuantidadeIdeal'].to_dict()

        # Combinar dados reais com ideais
        combined_data = []
        for item in real_data:
            unidade = item['Unidade']
            tdv = item['Tdv']
            quantidade = item['Quantidade']
            quantidade_ideal = ideal_dict.get((unidade, tdv), 0)  # 0 se não encontrado
            combined_data.append({
                'Tdv': tdv,
                'Unidade': unidade,
                'Quantidade': quantidade,
                'QuantidadeIdeal': quantidade_ideal
            })

        return jsonify({'report': combined_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500