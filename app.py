from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # type: ignore
import pandas as pd
from io import BytesIO
import logging
import os
from datetime import datetime
import glob

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as rotas

# Configura logging para depuração
logging.basicConfig(level=logging.DEBUG)

# Pasta para armazenar planilhas
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def serve_index():
    app.logger.debug("Acessando rota /")
    return send_from_directory('public', 'index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.debug("Recebida requisição para /upload")

    if 'file' not in request.files:
        app.logger.error("Nenhum arquivo enviado")
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['file']
    if file.filename is None or file.filename == '':
        app.logger.error("Nenhum arquivo selecionado")
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    if not file.filename.endswith('.xlsx'):
        app.logger.error("Arquivo não é .xlsx")
        return jsonify({'error': 'Arquivo deve ser .xlsx'}), 400

    try:
        # Nome do arquivo baseado na data atual
        today = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(UPLOAD_FOLDER, f'{today}.xlsx')

        # Verificar se já existe planilha para o dia
        if os.path.exists(file_path):
            app.logger.error("Planilha já existe para hoje")
            return jsonify({'error': 'Planilha já existe para hoje'}), 400

        # Salvar planilha
        file.save(file_path)
        app.logger.debug(f"Planilha salva em {file_path}")

        # Processar planilha
        data = pd.read_excel(file_path, engine='openpyxl')

        app.logger.debug("Verificando colunas")
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            missing = [
                col for col in required_columns if col not in data.columns
            ]
            app.logger.error(f"Colunas ausentes: {missing}")
            os.remove(file_path)  # Remove arquivo inválido
            return jsonify({'error': f"Colunas ausentes: {missing}"}), 400

        # Relatório: contagem de veículos por Marca
        report = data.groupby('Marca').size().to_dict()

        # Gráfico: contagem de veículos por Ano modelo
        chart_data = {
            'labels': data['Ano modelo'].value_counts().index.tolist(),
            'values': data['Ano modelo'].value_counts().values.tolist()
        }

        app.logger.debug("Retornando relatório e dados do gráfico")
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        app.logger.error(f"Erro ao processar arquivo: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/dates', methods=['GET'])
def get_dates():
    app.logger.debug("Recebida requisição para /dates")
    try:
        # Listar arquivos .xlsx na pasta uploads
        files = glob.glob(os.path.join(UPLOAD_FOLDER, '*.xlsx'))
        dates = [os.path.basename(f).replace('.xlsx', '') for f in files]
        dates.sort(reverse=True)  # Ordenar do mais recente ao mais antigo
        app.logger.debug(f"Datas disponíveis: {dates}")
        return jsonify({'dates': dates})
    except Exception as e:
        app.logger.error(f"Erro ao listar datas: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/report/<date>', methods=['GET'])
def get_report(date):
    app.logger.debug(f"Recebida requisição para /report/{date}")

    file_path = os.path.join(UPLOAD_FOLDER, f'{date}.xlsx')
    if not os.path.exists(file_path):
        app.logger.error(f"Planilha não encontrada para {date}")
        return jsonify({'error': f"Planilha não encontrada para {date}"}), 404

    try:
        data = pd.read_excel(file_path, engine='openpyxl')

        app.logger.debug("Verificando colunas")
        required_columns = ['Marca', 'Ano modelo']
        if not all(col in data.columns for col in required_columns):
            missing = [
                col for col in required_columns if col not in data.columns
            ]
            app.logger.error(f"Colunas ausentes: {missing}")
            return jsonify({'error': f"Colunas ausentes: {missing}"}), 400

        # Relatório: contagem de veículos por Marca
        report = data.groupby('Marca').size().to_dict()

        # Gráfico: contagem de veículos por Ano modelo
        chart_data = {
            'labels': data['Ano modelo'].value_counts().index.tolist(),
            'values': data['Ano modelo'].value_counts().values.tolist()
        }

        app.logger.debug("Retornando relatório e dados do gráfico")
        return jsonify({'report': report, 'chart': chart_data})
    except Exception as e:
        app.logger.error(f"Erro ao processar arquivo: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
