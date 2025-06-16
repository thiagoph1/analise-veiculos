from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user

login_bp = Blueprint('login', __name__)

# Importar dependências do app de forma tardia (usando uma função ou passando como argumento)
def init_login(app):
    from app import db, verify_password, User  # Importação tardia

    @login_bp.route('/', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if verify_password(username, password):
                user = User(username)
                login_user(user)
                return redirect(url_for('index.index'))
            else:
                flash('Usuário ou senha inválidos', 'error')
                return render_template('login.html', error='Usuário ou senha inválidos')

        return render_template('login.html')

# Inicializar o blueprint após o app estar pronto
init_login(None)  # Placeholder, será chamado pelo app.py