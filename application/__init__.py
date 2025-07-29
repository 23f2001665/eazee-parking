# application/__init__.py
from flask import Flask, url_for, redirect
from .config import DevConfig
# from .extensions import db, migrate, login_manager
from .extensions import db, login_manager
from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp
from .main import main_bp
from .database.models import User
import os


def create_app(config_object=DevConfig):
    app = Flask(__name__, template_folder="templates", static_folder="../static") # it won't be used as each bp have its own template folder.

    app.config.from_object(config_object)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.ico'))

    db.init_app(app)
    login_manager.init_app(app)
    # migrate.init_app(app, db)

    app.register_blueprint(main_bp, url_prefix="")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app  


# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# print("running form application/__init__")