from flask import Blueprint, jsonify
from flask_login import login_required
from routes.auth import get_db  # Importar a função de acesso

dates_bp = Blueprint('dates', __name__)

@dates_bp.route('/dates', methods=['GET'])
@login_required
def get_dates():
    try:
        db = get_db('veiculos_db')  # Acessar o banco veiculos_db
        collections = db.list_collection_names()
        dates = [col.replace('veiculos_', '').replace('_', '-') for col in collections if col.startswith('veiculos_')]
        dates.sort(reverse=True)
        return jsonify({'dates': dates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500