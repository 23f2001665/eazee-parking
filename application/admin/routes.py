from flask import render_template, flash, redirect, url_for, current_app, request
from flask_login import current_user, login_required

from functools import wraps
import datetime

from sqlalchemy import asc, desc, func

from . import admin_bp
from ..database.models import User, ParkingLot, ParkingSpot, Reservation
from .admin_forms import LotForm, EditProfileForm
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



@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Get the first 5 lots for the dashboard overview
    lots = ParkingLot.query.order_by(ParkingLot.name).limit(5).all()

    # Get the 5 most recent users (by creation date)
    users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template(
        'admin/admin_dashboard.html',
        lots=lots,
        users=users
    )


@admin_bp.route('/profile')
@login_required
@role_required('admin')
def profile():
    return render_template('admin/admin_profile_view.html', user=current_user)


@admin_bp.route('/summary')
@login_required
@role_required('admin')
def admin_summary():
    """
    Admin summary dashboard with system-wide statistics and charts
    """
    # Meta information for the top section
    total_users = User.query.count()
    active_users = User.query.filter(User.active_parking > 0).count()
    total_lots = ParkingLot.query.count()
    active_lots = ParkingLot.query.filter_by(is_active=True).count()
    total_system_revenue = db.session.query(func.sum(ParkingLot.total_revenue)).scalar() or 0
    total_reservations = Reservation.query.count()

    # Data for the revenue bar chart (Lot vs Revenue)
    lot_revenue_data = db.session.query(
        ParkingLot.name,
        ParkingLot.total_revenue
    ).order_by(ParkingLot.total_revenue.desc()).limit(10).all()  # Top 10 lots by revenue

    # Convert to list of dictionaries for JSON serialization
    revenue_chart_data = [
        {
            'name': lot_name,
            'revenue': float(revenue)
        }
        for lot_name, revenue in lot_revenue_data
    ]

    # Data for the pie chart (Occupied vs Free spots)
    total_spots = db.session.query(func.sum(ParkingLot.max_spots)).scalar() or 0
    occupied_spots = db.session.query(func.sum(ParkingLot.max_spots - ParkingLot.available_spots)).scalar() or 0
    free_spots = total_spots - occupied_spots

    spots_data = {
        'occupied': occupied_spots,
        'free': free_spots
    }

    return render_template(
        'admin/admin_summary.html',
        # Meta information
        total_users=total_users,
        active_users=active_users,
        total_lots=total_lots,
        active_lots=active_lots,
        total_system_revenue=total_system_revenue,
        total_reservations=total_reservations,
        # Chart data
        revenue_chart_data=revenue_chart_data,
        spots_data=spots_data
    )


@admin_bp.route('/all_lots')
@login_required
@role_required('admin')
def all_lots():
    sort = request.args.get('sort', 'name')
    order = request.args.get('order', 'asc')

    lots_query = ParkingLot.query

    if sort == 'name':
        lots_query = lots_query.order_by(
            asc(ParkingLot.name) if order == 'asc' else desc(ParkingLot.name)
        )
    elif sort == 'pincode':
        lots_query = lots_query.order_by(
            asc(ParkingLot.pincode) if order == 'asc' else desc(ParkingLot.pincode)
        )
    elif sort == 'spots':
        lots_query = lots_query.order_by(
            asc(ParkingLot.available_spots) if order == 'asc' else desc(ParkingLot.available_spots)
        )
    elif sort == 'price':
        lots_query = lots_query.order_by(
            asc(ParkingLot.cost_per_hour) if order == 'asc' else desc(ParkingLot.cost_per_hour)
        )
    elif sort == 'revenue':
        lots_query = lots_query.order_by(
            asc(ParkingLot.total_revenue) if order == 'asc' else desc(ParkingLot.total_revenue)
        )
    else:
        lots_query = lots_query.order_by(asc(ParkingLot.name))

    lots = lots_query.all()

    return render_template(
        'admin/all_lots.html',
        lots=lots,
        sort=sort,
        order=order
    )


@admin_bp.route('/view_lot_details/<int:lot_id>')
@login_required
@role_required('admin')
def view_lot_details(lot_id):
    # Get sort and order parameters from the request URL
    sort = request.args.get('sort', 'spot_number')  # Default sort by spot_number
    order = request.args.get('order', 'asc')  # Default ascending order

    lot = ParkingLot.query.get_or_404(lot_id)

    # Base query for spots in this lot
    spots_query = ParkingSpot.query.filter_by(lot_id=lot_id)

    # Apply sorting based on the 'sort' parameter
    if sort == 'id':
        spots_query = spots_query.order_by(
            asc(ParkingSpot.id) if order == 'asc' else desc(ParkingSpot.id)
        )
    elif sort == 'spot_number':
        spots_query = spots_query.order_by(
            asc(ParkingSpot.spot_number) if order == 'asc' else desc(ParkingSpot.spot_number)
        )
    elif sort == 'total_parking':
        spots_query = spots_query.order_by(
            asc(ParkingSpot.total_parking) if order == 'asc' else desc(ParkingSpot.total_parking)
        )
    elif sort == 'status':
        spots_query = spots_query.order_by(
            asc(ParkingSpot.status) if order == 'asc' else desc(ParkingSpot.status)
        )
    else:
        # Default fallback to spot_number if invalid sort parameter
        spots_query = spots_query.order_by(asc(ParkingSpot.spot_number))

    spots = spots_query.all()
    # spot_wise_reservation = [Reservation.query.filter_by(spot_id=spot.spot_id).all() for spot in spots]

    return render_template(
        'admin/view_lot_details.html',
        lot=lot,
        spots=spots,
        sort=sort,
        order=order
    )


@login_required
@role_required('admin')
@admin_bp.route('/details_reservation/<int:reservation_id>')
def details_reservation(reservation_id):

    reservation = db.session.get(Reservation, int(reservation_id))
    print(reservation)
    return render_template('admin/show_reservation_details.html', reservation=reservation)


@login_required
@role_required('admin')
@admin_bp.route("/add_lot", methods=["GET", "POST"])
def add_lot():
    form = LotForm()
    if form.validate_on_submit():
        # Create the ParkingLot instance
        try:
            new_lot = ParkingLot(
                name=form.name.data,
                cost_per_hour=form.cost_per_hour.data,
                address=form.address.data,
                pincode=form.pincode.data,
                max_spots=form.max_spots.data,
                available_spots=form.max_spots.data
            )
            db.session.add(new_lot)
            db.session.flush()  # flush so new_lot gets an ID without committing

            # Create ParkingSpot entries for this lot
            spot = None                 # to avoid name error if range is impossible
            for i in range(1, new_lot.max_spots + 1):
                spot = ParkingSpot(
                    spot_number=i,
                    lot_id=new_lot.id,
                    status="A",  # default: Available
                    total_parking=0
                )
                if spot:
                    db.session.add(spot)
            db.session.commit()
            flash("New Parking lot added!", "success")
            return redirect(url_for('admin.dashboard'))

        except Exception as e:
            flash(str(e), "danger")
            db.session.rollback()
            return redirect(url_for('admin.dashboard'))

    return render_template("admin/add_lot.html", form=form)


@login_required
@admin_bp.route("/edit-lot/<int:lot_id>", methods=["GET", "POST"])
@role_required('admin')
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    form = LotForm(obj=lot)

    if form.validate_on_submit():
        # Check for max_spot changes
        old_max = lot.max_spots
        new_max = form.max_spots.data

        lot.name = form.name.data
        lot.cost_per_hour = form.cost_per_hour.data
        lot.address = form.address.data
        lot.pincode = form.pincode.data
        lot.updated_at = datetime.datetime.utcnow()

        if new_max > old_max:
            # Add new spots
            # Step 1: Fetch all existing spot_numbers in one query
            existing_spots = db.session.query(ParkingSpot.spot_number).filter_by(lot_id=lot_id).all()
            existing_numbers = set(num for (num,) in existing_spots)

            # Step 2: Determine next k available spot numbers (fill gaps first)
            new_spots = []
            candidate = 1
            k = new_max - old_max

            while len(new_spots) < k:
                if candidate not in existing_numbers:
                    new_spots.append(candidate)
                candidate += 1

            # Step 3: Add all new spot objects in batch
            for spot_number in new_spots:
                spot = ParkingSpot(
                    lot_id=lot_id,
                    spot_number=spot_number,
                    status="A",
                    total_parking=0
                )
                db.session.add(spot)

            lot.available_spots += k

        elif new_max < old_max:
            # Handle spot removal only if the excess spots are available
            removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(old_max - new_max).all()
            # since we are using limit removable spot is always in safe range.

            if len(removable_spots) >= (old_max - new_max):      # this check is just to flash invalid shrink
                for spot in removable_spots:
                    db.session.delete(spot)
                lot.available_spots -= len(removable_spots)

            else:
                db.session.rollback()
                flash("Cannot reduce max spots: Some of the extra spots are currently occupied.", "danger")
                return render_template("admin/edit_lot.html", form=form, lot=lot)

        lot.max_spots = new_max

        try:
            db.session.commit()
            flash(f"Lot '{lot.name}' updated successfully.", "success")
            return redirect(url_for("admin.dashboard"))  # redirect to listing page
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")

    return render_template("admin/edit_lot.html", form=form, lot=lot)


@login_required
@admin_bp.route("/deactivate_lot/<int:lot_id>", methods=["POST"])
@role_required('admin')
def deactivate_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    try:
        if lot.is_active:
            lot.is_active = False
            db.session.commit()
            flash(f"Lot '{lot.name}' deactivated successfully.", "success")
            return redirect(url_for("admin.dashboard"))

        else:
            lot.is_active = True
            db.session.commit()
            flash(f"Lot '{lot.name}' has been activated again.", "success")
            return redirect(url_for("admin.view_lot_details", lot_id=lot_id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error occurred: {type(e).__name__}", "danger")

    return redirect(url_for("admin.dashboard"))




@admin_bp.route('/all_users')
@login_required
@role_required('admin')
def all_users():
    # Get sort and order parameters from the request URL
    sort = request.args.get('sort', 'username')  # Default sort by username
    order = request.args.get('order', 'asc')  # Default ascending order

    # Base query for all users
    users_query = User.query

    # Apply sorting based on the 'sort' parameter
    if sort == 'id':
        users_query = users_query.order_by(
            asc(User.id) if order == 'asc' else desc(User.id)
        )
    elif sort == 'username':
        users_query = users_query.order_by(
            asc(User.username) if order == 'asc' else desc(User.username)
        )
    elif sort == 'email':
        users_query = users_query.order_by(
            asc(User.email) if order == 'asc' else desc(User.email)
        )
    elif sort == 'total_parking':
        users_query = users_query.order_by(
            asc(User.total_parking) if order == 'asc' else desc(User.total_parking)
        )
    else:
        # Default fallback to username if invalid sort parameter
        users_query = users_query.order_by(asc(User.username))

    # Get all users with the applied sorting
    users = users_query.all()

    return render_template(
        'admin/all_users.html',
        users=users,
        sort=sort,
        order=order
    )


@admin_bp.route('/user_profile/<int:user_id>', methods=['GET'])
@login_required
def user_profile(user_id):
    user = User.query.get(user_id)
    return render_template('admin/user_profile.html', user=user)


@login_required
@admin_bp.route("/deactivate-user/<int:user_id>", methods=["GET", "POST"]) # remove get once template is ready
@role_required('admin')
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)

    # Check for active reservations
    has_active_reservation = Reservation.query.filter_by(user_id=user.id, status='O').first() is not None

    if has_active_reservation:
        flash(f"Cannot deactivate '{user.username}' — active reservations found.", "warning")
    else:
        if user.is_active:
            user.is_active = False
            flash(f"User '{user.username}' has been deactivated successfully.", "success")
        else:
            user.is_active = True
            flash(f"User '{user.username}' has been activated successfully.", "success")
        try:
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f"Database error while deactivating: {str(e)}", "danger")

    return redirect(url_for("admin.dashboard"))


