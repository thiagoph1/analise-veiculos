from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd

# Definir o Blueprint
tdv_report_bp = Blueprint('tdv_report', __name__)

@tdv_report_bp.route('/report/<date>/tdv', methods=['GET'])
@login_required
def get_tdv_report(date):
    from app import db  # Importar dentro da função

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