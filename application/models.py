from application.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    user_id  = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False) #always recieve a .lower()
    email = db.Column(db.String(100), unique=True, nullable=False)   #always recieve a .lower()
    phone = db.Column(db.String(10), unique=True, nullable=False)
    fullname = db.Column(db.String(50)), nullable=False)
    role = db.Column(db.String(5), default="user")                  #always recieve a .lower()
    password = db.Column(db.String(255), nullable=False)
    profile_pic_url = db.Column(db.String(255), default="")

    def __repr__(self):
        return f"hello from {self.username}"
