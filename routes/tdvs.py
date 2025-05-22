from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd

# Definir o Blueprint
tdvs_bp = Blueprint('tdvs', __name__)

@tdvs_bp.route('/tdvs/<date>', methods=['GET'])
@login_required
def get_tdvs(date):
    from app import db  # Importar dentro da função

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