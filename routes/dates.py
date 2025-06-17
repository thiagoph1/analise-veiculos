from flask import Blueprint, jsonify
from routes.auth import get_db  # Importar a função de acesso
from datetime import datetime

dates_bp = Blueprint('dates', __name__)

@dates_bp.route('/dates', methods=['GET'])
def get_dates():
    db = get_db('veiculos_db')  # Acessar o banco veiculos_db
    # Consultar valores únicos do campo "Data insert" na coleção veiculos
    dates = db.veiculos.distinct('Data insert')  # Ajuste 'veiculos' se o nome for diferente
    # Filtrar e formatar as datas (remover valores nulos e converter para string)
    date_list = [date for date in dates if date and isinstance(date, str)]
    print(f"Datas encontradas: {date_list}")  # Depuração
    return jsonify(date_list)