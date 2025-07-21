from flask import Blueprint, jsonify
from flask_login import login_required  # type: ignore
import pandas as pd
from routes.auth import get_db  # Importar a função de acesso

charts_bp = Blueprint('charts', __name__)

@charts_bp.route('/chart/<date>/disponibilidade', methods=['GET'])
@charts_bp.route('/chart/<date>/disponibilidade/<unit_filter>', methods=['GET'])
@login_required
def get_disponibilidade_chart(date, unit_filter=None):
    from app import ELOS_SISTRAN
    collection_name = f'veiculos_{date.replace("-", "_")}'  # Ex.: veiculos_2025_06_13
    collection = get_db('veiculos_db')[collection_name]
    if collection_name not in get_db('veiculos_db').list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    # Resto do código...

    try:
        data = pd.DataFrame(list(collection.find({}, {'_id': 0})))
        if 'Unidade' not in data.columns or 'Status Patrimonio' not in data.columns:
            missing = ['Unidade' if 'Unidade' not in data.columns else '', 'Status Patrimonio' if 'Status Patrimonio' not in data.columns else '']
            missing = [m for m in missing if m]
            return jsonify({'error': f'Colunas ausentes: {missing}'}), 400

        # Aplicar filtro de unidades
        if unit_filter == 'elos':
            data = data[data['Unidade'].isin(ELOS_SISTRAN)]
        elif unit_filter == 'extras':
            data = data[~data['Unidade'].isin(ELOS_SISTRAN)]

        if data.empty:
            return jsonify({'chart': {'labels': [], 'datasets': [{'label': 'Disponível', 'data': []}, {'label': 'Indisponível', 'data': []}]}}), 200

        # Definir categorias
        disponiveis = ['Em Uso', 'Em Trânsito', 'Estoque Interno']
        indisponiveis = ['Em Reparo', 'A Reparar', 'Inativo']

        # Criar coluna para categorizar status
        data['Categoria'] = data['Status Patrimonio'].apply(
            lambda x: 'Disponível' if x in disponiveis else 'Indisponível' if x in indisponiveis else 'Outros'
        )

        # Agrupar por Unidade e Categoria
        grouped = data.groupby(['Unidade', 'Categoria']).size().unstack(fill_value=0)

        # Garantir que Disponível e Indisponível existam
        if 'Disponível' not in grouped.columns:
            grouped['Disponível'] = 0
        if 'Indisponível' not in grouped.columns:
            grouped['Indisponível'] = 0

        # Calcular total por unidade (Disponível + Indisponível)
        grouped['Total'] = grouped['Disponível'] + grouped['Indisponível']

        # Ordenar por Total em ordem decrescente
        grouped = grouped.sort_values('Total', ascending=False)

        # Remover coluna Total para evitar interferência no gráfico
        grouped = grouped.drop(columns=['Total'])

        chart_data = {
            'labels': grouped.index.tolist(),
            'datasets': [
                {
                    'label': 'Disponível',
                    'data': [int(x) for x in grouped['Disponível'].tolist()],  # Converter int64 para int
                    'backgroundColor': 'rgba(34, 197, 94, 0.6)',
                    'borderColor': 'rgba(34, 197, 94, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Indisponível',
                    'data': [int(x) for x in grouped['Indisponível'].tolist()],  # Converter int64 para int
                    'backgroundColor': 'rgba(255, 99, 132, 0.6)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1
                }
            ]
        }
        return jsonify({'chart': chart_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@charts_bp.route('/chart/<date>/status_patrimonio', methods=['GET'])
@charts_bp.route('/chart/<date>/status_patrimonio/<unit_filter>', methods=['GET'])
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