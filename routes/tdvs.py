from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso

# Definir o Blueprint
tdvs_bp = Blueprint('tdvs', __name__)

@tdvs_bp.route('/tdvs/<date>', methods=['GET'])
@login_required
def get_tdvs(date):
    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = get_db('veiculos_db')[collection_name]
    
    if collection_name not in get_db('veiculos_db').list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0, 'Tdv': 1})))
        if 'Tdv' not in data.columns:
            return jsonify({'error': 'Coluna Tdv não encontrada'}), 400
        tdvs = sorted(data['Tdv'].dropna().unique().tolist())
        return jsonify({'tdvs': tdvs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500