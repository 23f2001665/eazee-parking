from .models import User, ParkingLot, ParkingSpot, Reservation
from ..extensions import db
from werkzeug.security import generate_password_hash as hash
import os, click, random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")

def create_admin(app):
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.drop_all()
        db.create_all()

        # Admin & Himanshu
        if not User.query.filter_by(username="admin").first():
            admin = User(
                username="admin",
                name="Admin User",
                gender="m",
                email="admin@mail.com",
                phone="9876543210",
                password=hash("admin@123"),
                role="admin"
            )
            db.session.add(admin)

        if not User.query.filter_by(username="himanshu").first():
            himanshu = User(
                username="himanshu",
                name="Himanshu",
                gender="m",
                email="himanshu@mail.com",
                phone="9335354585",
                password=hash("test@123"),
                address="Lucknow",
                pincode="226017"
            )
            db.session.add(himanshu)
        try:
            db.session.commit()
            click.echo("Admin & himanshu created")
        except Exception as e:
            db.session.rollback()
            print(e)
            print("Something went wrong in admin creation!")

        # Create lots
        lots = []
        for i in range(1, 6):
            lot = ParkingLot(
                name=f"Lot {i}",
                address=fake.address(),
                pincode=random.randint(100000, 999999),
                cost_per_hour=random.randint(10, 50),
                max_spots=10,
                available_spots=10
            )
            lots.append(lot)

        try:
            db.session.add_all(lots)
            db.session.commit()
            click.echo("sample lots created")
        except Exception as e:
            db.session.rollback()
            print(e)
            print("Something went wrong in lots creation!")

        # Create spots
        spots = []
        for lot in lots:
            for i in range(1, 11):
                spot = ParkingSpot(
                    lot_id=lot.id,
                    spot_number=i,
                    status="A",
                    total_parking=0
                )
                spots.append(spot)

        try:
            db.session.add_all(spots)
            db.session.flush()
            click.echo("sample spots in each lot created")
        except Exception as e:
            db.session.rollback()
            print(e)
            print("Something went wrong in spots creation!")

        # Create users
        users = []
        for i in range(10):
            name = fake.name()
            base = name.split()[0].lower()
            suffix = str(random.randint(1000, 9999))
            username = f"{base}{suffix}"
            email = f"{username}@example.com"
            phone = f"{random.choice(['6', '7', '8', '9'])}{random.randint(100000000, 999999999)}"

            user = User(
                username=username,
                name=name,
                gender=random.choice(["m", "f", "o"]),
                email=email,
                phone=phone,
                password=hash("password"),
            )
            users.append(user)

        try:
            db.session.add_all(users)
            db.session.commit()
            click.echo("sample users created")
        except Exception as e:
            db.session.rollback()
            print(e)
            print("Something went wrong in users creation!")

        # Create reservations
        # available_spots = ParkingSpot.query.filter_by(status="A").all()
        # random.shuffle(available_spots)
        # spot_idx = 0
        #
        # def create_reservation(user, spot):
        #     lot = spot.lot
        #
        #     is_ongoing = random.random() < 0.5
        #     now = datetime.utcnow()
        #     hours = random.randint(0, 5)
        #     start = now - timedelta(hours=hours)
        #     end = None if is_ongoing else start + timedelta(hours=hours)
        #
        #     reservation = Reservation(
        #         user_id=user.id,
        #         lot_id=lot.id,
        #         spot_number=spot.spot_number,
        #         start_time=start,
        #         end_time=end,
        #         vehicle_number=f"{random.choice(['MH', 'DL', 'KA'])}{random.randint(10,99)}AB{random.randint(1000,9999)}",
        #         cost_per_hr=lot.cost_per_hour,
        #         status="O" if is_ongoing else "C"
        #     )
        #     db.session.add(reservation)
        #
        #     # Update model counts
        #     user.total_parking += 1
        #     lot.total_parking += 1
        #     spot.total_parking += 1
        #     if is_ongoing:
        #         user.active_parking += 1
        #         lot.available_spots -= 1
        #         spot.status = "O"
        #
        #
        # try:
        #     for user in users:
        #         n = random.randint(1, 5)
        #         for _ in range(n):
        #             if spot_idx >= len(available_spots):
        #                 break
        #             spot = available_spots[spot_idx]
        #             create_reservation(user, spot)
        #             spot_idx += 1
        #
        #     # Commit the entire batch of reservations at the end
        #     db.session.commit()
        #     click.echo("✅ Fake data created successfully.")
        #
        # except Exception as e:
        #     # If anything goes wrong, roll back the entire batch
        #     db.session.rollback()
        #     click.echo(f"Error creating fake data: {type(e).__name__}: {e}")