from flask import Blueprint, jsonify
from flask_login import login_required # type: ignore
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso

status_patrimonio_chart_bp = Blueprint('status_patrimonio_chart', __name__)

@status_patrimonio_chart_bp.route('/chart/<date>/status_patrimonio', methods=['GET'])
@status_patrimonio_chart_bp.route('/chart/<date>/status_patrimonio/<unit_filter>', methods=['GET'])
@login_required
def get_status_patrimonio_chart(date, unit_filter=None):
    from app import ELOS_SISTRAN  # Importar dentro da função para evitar ciclo
    
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
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