from flask import Blueprint, request, render_template, redirect, url_for
from flask_login import login_user

# Definir o Blueprint
login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import users, User  # Importar dentro da função
    import bcrypt

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            return render_template('login.html', error='Usuário e senha são obrigatórios'), 400
        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]):
            user = User(username)
            login_user(user)
            return redirect(url_for('index.index'))
        return render_template('login.html', error='Credenciais inválidas'), 401
    return render_template('login.html', error=None)