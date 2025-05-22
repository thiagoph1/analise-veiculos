from flask import Blueprint, jsonify
from flask_login import login_required

# Definir o Blueprint
dates_bp = Blueprint('dates', __name__)

@dates_bp.route('/dates', methods=['GET'])
@login_required
def get_dates():
    from app import db  # Importar dentro da função

    try:
        collections = db.list_collection_names()
        dates = [col.replace('veiculos_', '').replace('_', '-') for col in collections if col.startswith('veiculos_')]
        dates.sort(reverse=True)
        return jsonify({'dates': dates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500