from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
# migrate = Migrate()
login_manager = LoginManager()

# Safe, context-free event hook for SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Enable only if using SQLite
    if dbapi_connection.__class__.__module__.startswith("sqlite3"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # print("FK Enforcement is:", "ON" if cursor.fetchone()[0] else "OFF")
        cursor.close()

# Optional: Flask-Login defaults
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"
