from flask import Blueprint, jsonify, request
from flask_login import login_required
from routes.auth import get_db  # Importar a função de acesso
from app import ELOS_SISTRAN  # Importar a constante de app.py

disponibilidade_chart_bp = Blueprint('disponibilidade_chart', __name__)

@disponibilidade_chart_bp.route('/chart/<date>/disponibilidade', methods=['GET'])
@disponibilidade_chart_bp.route('/chart/<date>/disponibilidade/<unit_filter>', methods=['GET'])
@login_required
def get_disponibilidade_chart(date, unit_filter=None):
    try:
        db = get_db('veiculos_db')  # Acessar o banco veiculos_db
        collection_name = f'veiculos_{date.replace("-", "_")}'  # Ex.: veiculos_2025_05_12
        collection = db[collection_name]

        # Filtro de unidade
        unit_filter = unit_filter if unit_filter else 'all'
        if unit_filter != 'all' and unit_filter not in ELOS_SISTRAN + ['extras']:
            return jsonify({'error': 'Filtro de unidade inválido'}), 400

        # Consultar dados (exemplo: contar veículos disponíveis e indisponíveis)
        pipeline = [
            {'$match': {'Ativo': 'S'}},  # Filtrar veículos ativos
            {'$group': {
                '_id': '$Status Patrimonio',
                'count': {'$sum': 1}
            }}
        ]
        if unit_filter == 'all':
            results = collection.aggregate(pipeline)
        elif unit_filter == 'elos':
            results = collection.aggregate(pipeline + [{'$match': {'Unidade': {'$in': ELOS_SISTRAN}}}])
        elif unit_filter == 'extras':
            results = collection.aggregate(pipeline + [{'$match': {'Unidade': {'$nin': ELOS_SISTRAN}}}])

        chart_data = {'labels': [], 'datasets': [{'data': [], 'label': 'Disponível'}, {'data': [], 'label': 'Indisponível'}]}
        for result in results:
            status = result['_id']
            count = result['count']
            if status in ['Em Uso', 'Disponível']:  # Ajuste conforme os valores reais
                chart_data['datasets'][0]['data'].append(count)
                chart_data['labels'].append(status)
            else:
                chart_data['datasets'][1]['data'].append(count)
                chart_data['labels'].append(status)

        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500