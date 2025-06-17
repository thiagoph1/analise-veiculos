from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso

tdv_unidade_report_bp = Blueprint('tdv_unidade_report', __name__)

@tdv_unidade_report_bp.route('/report/<date>/tdv_unidade', methods=['GET'])
@tdv_unidade_report_bp.route('/report/<date>/tdv_unidade/<tdv>', methods=['GET'])
@login_required
def get_tdv_unidade_report(date, tdv=None):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
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