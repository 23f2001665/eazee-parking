from sqlite3 import IntegrityError

from flask_login import UserMixin
from datetime import datetime
from math import ceil
from sqlalchemy import CheckConstraint, event
from sqlalchemy.orm import validates, foreign

from application.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(5), default="user")
    is_active = db.Column(db.Boolean, default=True)

    # user login details
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(64), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(10), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)          # will be used in future

    # user profile detail
    name = db.Column(db.String(64), nullable=False)
    gender = db.Column(db.String(1))                   # m, f and o
    address = db.Column(db.String(255))
    pincode = db.Column(db.String(6))
    avatar_url = db.Column(db.String(255), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


    # reservation details
    total_parking = db.Column(db.Integer, default=0)
    active_parking = db.Column(db.Integer, default=0)

    # relations
    reservations = db.relationship("Reservation", back_populates="user", lazy=True)

    # constraints
    __table_args__ = (
        CheckConstraint("role in ('user', 'admin')", name="check_role"),
        CheckConstraint("LENGTH(pincode) = 6", name="check_pincode"),
        CheckConstraint("gender IN ('m', 'f', 'o')", name="check_gender"),
        CheckConstraint("active_parking >= 0", name="check_active_parking_non_negative"),
        CheckConstraint("total_parking >= 0", name="check_total_parking_non_negative"),
        CheckConstraint("total_parking >= active_parking", name="check_total_gt_active"),
    )

    # methods
    def __repr__(self):
        return f"<User {self.username} (ID: {self.id})>"

    __str__ = __repr__


class ParkingLot(db.Model):
    __tablename__ = "parking_lot"
    id = db.Column(db.Integer, primary_key=True)

    # lot details
    name = db.Column(db.String(60), nullable=False)
    cost_per_hour = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.String(6), nullable=False, index=True)
    max_spots = db.Column(db.Integer, default=20, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False, default=20)

    # admin stuff
    is_active = db.Column(db.Boolean, default=True)                 # will be used for soft delete
    total_parking = db.Column(db.Integer, nullable=False, default=0)                        # total parking of all time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    total_revenue = db.Column(db.Numeric(10, 2), nullable=True, index=True, default=0)         # make it not nullable later if possible

    # constraints
    __table_args__ = (
        db.UniqueConstraint('name', 'pincode', name='uq_lot_name_pincode'),
        CheckConstraint("total_parking >= 0", name="check_total_parking_non_negative"),
        CheckConstraint("cost_per_hour >= 0", name="check_parking_lot_cost_per_hour"),
        CheckConstraint("available_spots >= 0", name="check_available_spots_non_negative"),
        CheckConstraint("max_spots >= 0", name="check_max_spots_non_negative"),
        CheckConstraint("max_spots >= available_spots", name="check_max_gt_available_spots"),
        CheckConstraint("LENGTH(pincode) = 6", name="check_pincode"),
    )

    # relationships
    spots = db.relationship("ParkingSpot", back_populates="lot", cascade="all, delete-orphan", lazy=True)
    reservations = db.relationship("Reservation", back_populates="lot", lazy=True)

    # methods
    def __repr__(self):
        return f"<Lot {self.name} (ID: {self.id}, ₹{self.cost_per_hour}/hr) \tAvailable Spots: {self.available_spots} \tTotal Parking: {self.total_parking}>"

    __str__ = __repr__


class ParkingSpot(db.Model):
    __tablename__ = "parking_spot"
    id = db.Column(db.Integer, primary_key=True)

    # spot details
    spot_number= db.Column(db.Integer, nullable=False, index=True)
    status = db.Column(db.String(1), default="A", nullable=False, index=True)
    total_parking = db.Column(db.Integer, nullable=False, default=0)            # total parking of all time

    # constraints
    __table_args__ = (
        db.UniqueConstraint("lot_id", "spot_number", name="uix_lot_spot_number"),
        CheckConstraint("spot_number>= 0", name="check_spot_number_non_negative"),
        CheckConstraint("status IN ('O', 'A')", name="check_status"),
        CheckConstraint("total_parking >= 0", name="check_total_parking_non_negative"),
    )
    # week relational attribute
    reservation_id = db.Column(db.Integer, nullable=True, index=True)
    # foreign keys and relationships
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), nullable=False, index=True)
    lot = db.relationship("ParkingLot", back_populates="spots")

    # methods
    def __repr__(self):
        status = "Occupied" if self.status == "O" else "Available"
        return f"<Spot #{self.id, self.spot_number} in Lot {self.lot.name if self.lot else "Lot Number not visible"} [status={status}]>"

    __str__ = __repr__

@event.listens_for(ParkingSpot, "before_delete")
def prevent_delete_if_occupied(mapper, connection, target):
    print("from 132")
    if target.status == "O":
        print("from 134")
        raise IntegrityError(None, None, "Cannot delete an occupied spot.")

class Reservation(db.Model):
    """
    Reservation table will maintain history while spot's won't,
    this can lead very inconsistent states.
    For this reason I am remove foreign keys from spot_id.
    Hence, breaking the sync between Reservation table and Spots table.
    But this approach can only be applied if I write routes very carefully,
    Making sure no reservation attain inconsistent  or impossible states.
    """
    __tablename__ = "reservation"
    id = db.Column(db.Integer, primary_key=True)

    #reservation details
    status = db.Column(db.String(1), default="O", nullable=False, index=True)  # 'O' or 'C' occupied or completed
    cost_per_hr = db.Column(db.Numeric(10, 2), nullable=False)                  # set at reservation time
    vehicle_number = db.Column(db.String(12), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)

    # week relational attribute
    spot_number = db.Column(db.Integer, nullable=False, index=True)  # no sync

    # foreign keys
    # spot_id = db.Column(db.Integer, db.ForeignKey("parking_spot.id"), index=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True, nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), index=True, nullable=False)

    user = db.relationship("User", back_populates="reservations")
    lot = db.relationship("ParkingLot", back_populates="reservations", lazy=True)

    # constraints
    __table_args__ = (
        CheckConstraint("status IN ('O', 'C')", name="check_status"),
        CheckConstraint("cost_per_hr >= 0", name="check_cp_hr_non_negative"),
        CheckConstraint("LENGTH(vehicle_number) BETWEEN 6 AND 12", name="check_vehicle_number_len"),
        # CheckConstraint("end_time >= start_time", name="check_end_time_non_negative"),  fails if end_time not defined
    )

    # methods
    @property
    def total_cost(self):
        if self.end_time is None:
            duration = (datetime.utcnow() - self.start_time).total_seconds() / 3600
        else:
            duration = (self.end_time - self.start_time).total_seconds() / 3600
        return round(float(self.cost_per_hr) * ceil(duration), 2)

    def __repr__(self):
        if self.end_time:
            return f"<Reservation {self.id}: Spot {self.spot_number} by User {self.user_id} for Vehicle: {self.vehicle_number
            } from {self.start_time} to {self.end_time}>"
        return f"<Reservation {self.id}: Spot {self.spot_number} by User {self.user_id} for Vehicle: {self.vehicle_number
        } starting {self.start_time} STILL OCCUPIED >"


