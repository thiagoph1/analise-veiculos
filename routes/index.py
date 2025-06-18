from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user  # type: ignore
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso

index_bp = Blueprint('index', __name__)  # Blueprint principal

@index_bp.route('/home')  # Defina a rota diretamente
@login_required
def index():
    print(f"Página index carregada para usuário: {current_user.id}")  # Depuração
    return render_template('index.html')

#Busca das TDV no MongoDB
@index_bp.route('/tdvs/<date>', methods=['GET'])
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


#Busca das Datas no MongoDB
@index_bp.route('/dates', methods=['GET'])
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