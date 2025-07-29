from . import main_bp
from flask import render_template


@main_bp.route('/')
@main_bp.route('/index')
@main_bp.route('/home')
@main_bp.route('/main/home')
def home():
    return render_template("index.html")