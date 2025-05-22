from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd

# Definir o Blueprint
report_bp = Blueprint('report', __name__)

@report_bp.route('/report/<date>', methods=['GET'])
@login_required
def get_report(date):
    from app import db  # Importar dentro da função

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