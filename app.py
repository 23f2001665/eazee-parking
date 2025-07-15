from flask import Flask
from application import models, init_db
from application.database import db
from pathlib import Path

def create_app():
    app = Flask(__name__)
    db_file = Path(app.instance_path) / "parking.sqlite3"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_file}"
    db.init_app(app)
    
    db_file.parent.mkdir(parents=True, exist_ok=True)  #  ensure instance/ exists

    with app.app_context():
        try:
            if not db_file.exists():
                print("doesn't exist")
                
                init_db.create_admin(app)
            else:
                admin = models.User.query.filter_by(role='admin').first()
                if not admin:
                    db.drop_all()
                    print("db dropped")
                    init_db.create_admin(app)
        except Exception as exc:
            print("Some error occured in databse creation in app.py line 13", exc)

    return app

if __name__ == "__main__":
    # total wipeout command, just for testing purposes.
    from utils import remove
    remove.remove(auto=True)

    app = create_app()
    app.run(debug=True)
