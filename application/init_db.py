from application.models import *
from application.database import db
from werkzeug.security import generate_password_hash as hash
from flask import url_for
# from faker import Faker

# # Faker setup
# fake = Faker("en_IN")
# fake.seed_instance(42)

#admin and users creation, this runs when users table is without admin or doesn't exist.
def create_admin(app):
    db.create_all()
    with app.app_context(), app.test_request_context():
        admin_image = url_for("static", filename="images/admin.jpg", _external=True)
        user_image = url_for("static", filename="images/default_user.jpg", _external=True)

    #admin creation
    admin = User(username="admin", role="admin", phone="9999599990",
                fullname="admin", email="admin@mail.com", password=hash("Admin@123"),
                profile_pic_url=admin_image)
    db.session.add(admin)
    print("admin created")

    #user creation    
    himanshu = User(username="himanshu", phone="9090909090",
                fullname="himanshu", email="himanshu@mail.com", password=hash("himanshu@123"),
                profile_pic_url=user_image)
    db.session.add(himanshu)
    print(himanshu)
    db.session.commit()


