# app.py

from application import create_app
from application.extensions import db
from application.database.init_db import create_admin
from flask.cli import with_appcontext
import click

app = create_app()

@app.shell_context_processor
def _shell_context():
    from application.database import User, ParkingLot, ParkingSpot, Reservation
    return dict(db=db, User=User, ParkingLot=ParkingLot, ParkingSpot=ParkingSpot, Reservation=Reservation)


# Example custom CLI: flask seed
@click.command("seed")
@with_appcontext
def seed():
    create_admin(app)


@click.command("clear-data")
@with_appcontext
def clear_data():
    
    # Get all tables in correct deletion order (child → parent)
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f"🗑️ Deleting from {table.name}...")
        db.session.execute(table.delete())

    db.session.commit()
    click.echo("all tables cleared successfully")


@click.command("drop-all")
@with_appcontext
def drop_all():
    db.drop_all()
    click.echo("deleted all the schemas")


app.cli.add_command(clear_data)
app.cli.add_command(seed)
app.cli.add_command(drop_all)

if __name__ == "__main__":
    app.run(debug=True)
    # don't call seed from here it is meant to be called from flash shell only.