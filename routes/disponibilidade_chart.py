from flask import Blueprint, jsonify
from flask_login import login_required
import pandas as pd

# Definir o Blueprint
disponibilidade_chart_bp = Blueprint('disponibilidade_chart', __name__)

@disponibilidade_chart_bp.route('/chart/<date>/disponibilidade', methods=['GET'])
@disponibilidade_chart_bp.route('/chart/<date>/disponibilidade/<unit_filter>', methods=['GET'])
@login_required
def get_disponibilidade_chart(date, unit_filter=None):
    from app import db, ELOS_SISTRAN  # Importar dentro da função

    collection_name = f'veiculos_{date.replace("-", "_")}'
    collection = db[collection_name]
    
    if collection_name not in db.list_collection_names():
        return jsonify({'error': 'Data não encontrada'}), 404
    
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
        
        # Log para depuração
        print("Valores únicos em Unidade após filtro:", data['Unidade'].unique().tolist())
        
        # Definir categorias
        disponiveis = ['Em Uso', 'Em Trânsito', 'Estoque Interno']
        indisponiveis = ['A Alienar', 'Em Reparo', 'A Reparar', 'Inativo']
        
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
        
        # Log para depuração
        print("Dados agrupados:", grouped.to_dict())
        
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
        print("Erro na rota /disponibilidade:", str(e))
        return jsonify({'error': str(e)}), 500