from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user
from routes.auth import User, verify_password  # Importar de auth.py

login_bp = Blueprint('login', __name__)

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