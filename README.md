# Análise de Viaturas

Sistema para gerenciar e analisar dados de viaturas da Aeronáutica, com armazenamento no MongoDB Cloud, interface web em Flask e geração de relatórios/gráficos.

## Requisitos
- Python 3.9+
- Dependências: `pandas`, `pymongo`, `flask`, `openpyxl`
- MongoDB Cloud
- Render para deploy

## Estrutura das Planilhas
- Formato: XLSX
- Campos (29): planilha geral de viaturas, ...

## Como Executar
1. Clone o repositório.
2. Instale dependências: `pip install -r requirements.txt`
3. Configure a variável de ambiente `MONGODB_URI`.
4. Execute o script de upload: `python scripts/upload_to_mongodb.py uploads/viaturas_YYYY-MM-DD.xlsx`
5. Inicie o Flask: `flask run`

## Deploy no Render
- Crie um serviço Web no Render.
- Configure as variáveis de ambiente (`MONGODB_URI`, `FLASK_ENV`).
- Use o comando `gunicorn app:app` para iniciar o servidor.
