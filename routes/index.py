from flask import Blueprint, current_app
from flask_login import login_required

# Definir o Blueprint
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
@login_required
def index():
    return current_app.send_static_file('index.html')