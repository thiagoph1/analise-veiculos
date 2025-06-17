from flask import Blueprint, render_template
from flask_login import login_required, current_user # type: ignore

index_bp = Blueprint('index', __name__)  # Remova url_prefix='/home' aqui

@index_bp.route('/home')  # Defina a rota diretamente
@login_required
def index():
    print(f"Página index carregada para usuário: {current_user.id}")  # Depuração
    return render_template('index.html')