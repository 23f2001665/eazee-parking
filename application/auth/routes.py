from datetime import datetime

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from sqlalchemy.sql.functions import current_user

from . import auth_bp  # importing the Blueprint object
from ..database.models import User
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import ForgotPasswordForm, LoginForm, RegisterForm


# print("printing from auth.routes")

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('auth/login.html', form=LoginForm())

    elif request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            id_type = form.id_type.data
            id_value = form.id_value.data
            password = form.password.data

            if id_type == "username":
                user = User.query.filter_by(username=id_value).first()
                if user and check_password_hash(user.password, password) and user.is_active:
                    login_user(user)
                    user.last_login = datetime.utcnow()
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('user.dashboard' if user.role=='user' else 'admin.dashboard'))
                else:
                    flash("Invalid Credentials")
                    return redirect(url_for('auth.login'))

            elif id_type == "email":
                user = User.query.filter_by(email=id_value).first()
                if user and check_password_hash(user.password, password) and user.is_active:
                    login_user(user)
                    user.last_login = datetime.utcnow()
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('admin.dashboard' if user.role=='admin' else 'user.dashboard'))
                else:
                    flash("Invalid Credentials")
                    return redirect(url_for('auth.login'))

            elif id_type == "phone":
                user = User.query.filter_by(phone=id_value).first()
                if user and check_password_hash(user.password, password) and user.is_active:
                    login_user(user)
                    user.last_login = datetime.utcnow()
                    db.session.add(user)
                    db.session.commit()
                    return redirect(url_for('admin.dashboard' if user.role=='admin' else 'user.dashboard'))
                else:
                    flash("Invalid Credentials")
                    return redirect(url_for('auth.login'))
        else:
            flash("Validation Failed! Invalid Credentials")
            return redirect(url_for('auth.login'))





@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()
        phone = form.phone.data.strip()
        name = form.name.data.strip()
        gender = form.gender.data
        address = form.address.data.strip()
        pincode = form.pincode.data.strip()
        password = form.password.data

        # Uniqueness checks
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
        elif User.query.filter_by(phone=phone).first():
            flash("Phone already exists", "danger")
        else:
            try:
                password_hash = generate_password_hash(password)
                user = User(username=username, email=email, phone=phone,
                            name=name, gender=gender, address=address,
                            pincode=pincode, password=password_hash)
                db.session.add(user)
                db.session.commit()
                flash("User created successfully. Please log in.", "success")
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                print("Error creating user:", e)
                flash(f"Something went wrong. Try again. {e.__class__.__name__}", "danger")
        return redirect(url_for('auth.login'))
    else:
        if request.method == "POST":
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.capitalize()}: {error}", "warning")
                    return "Error in registration. Please try again.", 500

        return render_template("auth/register.html", form=form)



@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('logout successfully!')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        print("validated")
        email = form.email.data
        username = form.username.data
        new_password = form.new_password.data
        user = User.query.filter_by(username=username).first()

        if user and user.email == email and user.is_active:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash("Password reset successful!", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("Invalid username or email", "danger")
            return redirect(url_for('auth.login'))

    else:
        if request.method == "POST":
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field.capitalize()}: {error}", "warning")

    # Always render the form if GET or failed POST
        return render_template('auth/forgot.html', form=form)
