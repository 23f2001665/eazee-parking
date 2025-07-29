from functools import wraps

from flask import render_template, request, flash, redirect, url_for,  current_app
from flask_login import current_user, login_required, logout_user

import os, datetime
from werkzeug.utils import secure_filename
from sqlalchemy import asc, desc, func, case
from sqlalchemy.orm import joinedload

from . import user_bp
from ..database.models import User, Reservation, ParkingLot, ParkingSpot
from .user_forms import EditProfileForm
from ..extensions import db


def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in first.", "warning")
                return redirect(url_for('auth.login'))

            if current_user.role != role:
                flash("Access denied.", "danger")
                return redirect(url_for('user.dashboard'))  # or home page

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route("/dashboard")
@user_bp.route('/')
@login_required
def dashboard():
    user = current_user
    lots = ParkingLot.query.filter(ParkingLot.available_spots > 0, ParkingLot.is_active==True).limit(4).all()
    reservations = Reservation.query.filter(Reservation.user_id == user.id).order_by(Reservation.end_time).limit(4)
    if user:
        return render_template('user/dashboard.html', lots=lots, reservations=reservations)
    else:
        return 'Data Not Found.<br><a href="/">home</a>' # I think this file will never be display login will handle this.


@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(username=current_user.username).first()
    return render_template('user/user_profile_view.html', user=user)


@role_required('user')
@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        # Update regular fields
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        current_user.gender = form.gender.data
        current_user.address = form.address.data
        current_user.pincode = form.pincode.data

        # Handle optional avatar upload
        file = form.avatar.data  # Not using request.files directly

        if file:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            new_path = os.path.join(upload_folder, filename)

            # Create folder if it doesn't exist
            os.makedirs(upload_folder, exist_ok=True)

            # Delete old image if it's not the default one
            old_path = os.path.join(upload_folder, os.path.basename(current_user.avatar_url or ""))
            if os.path.exists(old_path) and "default_user.jpeg" not in old_path:
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"Error deleting old file: {e}")

            # Save new image
            file.save(new_path)

            current_user.avatar_url = f"/static/uploads/{filename}"

        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for("user.profile"))

    return render_template('user/edit_profile.html', form=form, user=current_user)



@user_bp.route("/summary")
@login_required
def user_summary():
    # Reservation count
    total_reservations = Reservation.query.filter_by(user_id=current_user.id).count()
    active_reservations = Reservation.query.filter_by(user_id=current_user.id, status='O').count()

    # Status breakdown
    status_counts = (
        db.session.query(Reservation.status, func.count())
        .filter(Reservation.user_id == current_user.id)
        .group_by(Reservation.status)
        .all()
    )
    status_data = {status: count for status, count in status_counts}

    # Reservations by lot with active/completed breakdown for stacked chart
    lot_stats_raw = (
        db.session.query(
            ParkingLot.name,
            func.sum(case((Reservation.status == 'O', 1), else_=0)).label('active_count'),
            func.sum(case((Reservation.status == 'C', 1), else_=0)).label('completed_count')
        )
        .join(Reservation, Reservation.lot_id == ParkingLot.id)
        .filter(Reservation.user_id == current_user.id)
        .group_by(ParkingLot.name)
        .order_by(ParkingLot.name)
        .all()
    )

    # Convert Row objects to a list of dictionaries for JSON serialization
    lot_stats = [
        {
            'name': row[0],
            'active_count': int(row[1]) if row[1] else 0,
            'completed_count': int(row[2]) if row[2] else 0
        }
        for row in lot_stats_raw
    ]

    return render_template(
        "user/user_summary.html",
        total_reservations=total_reservations,
        active_reservations=active_reservations,
        status_data=status_data,
        lot_stats=lot_stats
    )



@user_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if request.form.get("confirm_delete"):
        user = current_user
        if user.active_parking == 0:
        # Set inactive first
            user.is_active = False
            db.session.commit()  # Don't forget this
            logout_user()  # Now logout safely
        else:
            flash("You have some active parking, free them before deleting your account.", "warning")
            return redirect(url_for("user.profile"))

        flash("Your account has been deleted.", "success")
        return redirect(url_for('auth.login'))

    flash("You must confirm account deletion.", "danger")
    return redirect(url_for('user.profile'))


@user_bp.route('/all_lots')
def all_lots():
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    lots = ParkingLot.query

    if sort == 'name':
        lots = lots.order_by(ParkingLot.name.asc() if order == 'asc' else ParkingLot.name.desc())
    elif sort == 'pincode':
        lots = lots.order_by(ParkingLot.pincode.asc() if order == 'asc' else ParkingLot.pincode.desc())
    elif sort == 'spots':
        lots = lots.order_by(ParkingLot.available_spots.asc() if order == 'asc' else ParkingLot.available_spots.desc())
    elif sort == 'price':
        lots = lots.order_by(ParkingLot.cost_per_hour.asc() if order == 'asc' else ParkingLot.cost_per_hour.desc())

    return render_template("user/show_all_lots.html", lots=lots.all(), sort=sort, order=order)


@user_bp.route('/all_reservations')
@login_required
def all_reservations():
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    reservations_query = Reservation.query.filter_by(user_id=current_user.id)

    if sort == 'lot_name':
        reservations_query = reservations_query.join(ParkingLot).order_by(
            asc(ParkingLot.name) if order == 'asc' else desc(ParkingLot.name)
        )
    elif sort == 'start_time ':
        reservations_query = reservations_query.order_by(
            asc(Reservation.start_time ) if order == 'asc' else desc(Reservation.start_time )
        )
    elif sort == 'end_time ' or 1==1:       # it is else block as well
        reservations_query = reservations_query.order_by(asc(Reservation.end_time) if order == 'asc' else desc(Reservation.end_time))

    reservations = reservations_query.options(joinedload(Reservation.lot)).all()

    return render_template(
        'user/show_all_reservations.html', reservations=reservations, sort=sort, order=order)


@user_bp.route('/details_reservation/<int:reservation_id>')
@login_required
def details_reservation(reservation_id):

    reservation = Reservation.query.filter_by(
        id=reservation_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template('user/show_reservations_details.html', reservation=reservation)


@user_bp.route('/book_lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
def book_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    if lot.available_spots <= 0 and not lot.is_active:
        flash("You can't book that's not available.", "warning")
        return redirect(url_for('user.all_lots'))
    if request.method == 'GET':
        return render_template('user/book_parking.html', lot=lot)
    else:
        vehicle_number = request.form.get('vehicle_number')
        spot = db.session.query(ParkingSpot).filter_by(lot_id=lot_id, status='A').with_for_update(skip_locked=True).first()

        if not spot:
            flash("No available spots in this lot.", "danger")
            return redirect(url_for('user.all_lots'))

        reservation = Reservation(
            user_id=current_user.id,
            lot_id=lot_id,
            vehicle_number=vehicle_number,
            spot_number=spot.spot_number,
            cost_per_hr=lot.cost_per_hour,
        )
        db.session.add(reservation)
        db.session.commit()

        spot.status = 'O'
        spot.reservation_id = reservation.id
        spot.total_parking += 1
        lot.available_spots -= 1
        lot.total_parking += 1
        current_user.total_parking += 1
        current_user.active_parking += 1

        try:
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation successful!", "success")
            return redirect(url_for('user.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong while reserving. Please try again.", "danger")
            return redirect(url_for('user.dashboard'))



@user_bp.route('/free_reservation/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def free_reservation(reservation_id):

    # Find the specific reservation for the current user, or return 404
    reservation = Reservation.query.filter_by(id=reservation_id, user_id=current_user.id).first_or_404()

    # Prevent re-freeing an already completed reservation
    if reservation.status == 'C' or reservation.end_time is not None:

        flash('This reservation has already been completed.', 'warning')
        return redirect(url_for('user.details_reservation', reservation_id=reservation.id))

    if request.method == 'POST':
        try:

            # 1. update reservation
            reservation.status = 'C'                # completed
            reservation.end_time = datetime.datetime.utcnow()

            # 2. update spot & lot
            spot = db.session.query(ParkingSpot).filter_by(spot_number=reservation.spot_number, lot_id=reservation.lot_id).first()
            spot.status = 'A'
            # print(spot)
            spot.reservation_id = None
            reservation.lot.total_revenue = float(reservation.lot.total_revenue) + reservation.total_cost
            reservation.lot.available_spots += 1

            # 3. update user
            reservation.user.active_parking -= 1        # he/she freed one parking

            # 4. commit
            db.session.commit()

            flash(f'Checkout successful for Spot #{reservation.spot_number}! Thank you.', 'success')
            return redirect(url_for('user.dashboard'))

        except Exception as e:
            print("in except block")
            db.session.rollback()
            print(e)
            flash(f'An error occurred during checkout: {e.with_traceback(None)}', 'danger')
            return redirect(url_for('user.all_reservations'))

    # For a GET request, just show the confirmation page
    return render_template('user/free_reservation.html', reservation=reservation)

