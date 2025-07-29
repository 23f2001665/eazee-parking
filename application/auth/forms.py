from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Regexp, Length, EqualTo

class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(),
        Email(message="Invalid email"),
        Regexp(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", message="Invalid email format")
    ], render_kw={ "placeholder": "Enter your email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "title": "Enter a valid email like user@example.com"
    })

    username = StringField("Username", validators=[
        DataRequired(),
        Regexp(r"^[a-zA-Z0-9_.-]{3,20}$", message="Username must be 3–20 characters long and alphanumeric")
    ], render_kw={ "placeholder": "Enter your username",
        "pattern": r"^[a-zA-Z0-9_.-]{3,20}$",
        "title": "3–20 chars: letters, numbers, underscore, dot, or hyphen"
    })

    new_password = PasswordField("New Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ], render_kw={ "placeholder": "Enter your new password",
        "pattern": r".{6,}",
        "title": "Password must be at least 6 characters long"
    })

    submit = SubmitField("Submit")



class LoginForm(FlaskForm):
    id_type = SelectField("Login with", choices=[
        ("username", "Username"),
        ("email", "Email"),
        ("phone", "Phone")
    ], validators=[DataRequired()])

    id_value = StringField("ID", validators=[
        DataRequired(),
        Regexp(
            r"^[a-zA-Z0-9_.+-@]+$",
            message="Enter a valid ID (no spaces or special characters except . _ - + @)"
        )
    ], render_kw={
        "placeholder": "Enter your ID (email, username, or phone)",
        "pattern": r"^[a-zA-Z0-9_.+-@]+$",
        "title": "No spaces, only letters, digits and . _ - + @"
    })

    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ], render_kw={
        "placeholder": "Enter your password",
        "pattern": r".{6,}",
        "title": "Password must be at least 6 characters long"
    })

    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(),
        Regexp(r"^[a-zA-Z0-9_.-]{3,20}$", message="3–20 alphanumeric/underscore/dash/dot allowed")
    ], render_kw={
        "placeholder": "Enter username",
        "pattern": r"^[a-zA-Z0-9_.-]{3,20}$",
        "title": "3–20 characters: letters, digits, underscore, dot or dash"
    })

    email = StringField("Email", validators=[
        DataRequired(),
        Email(message="Invalid email"),
    ], render_kw={
        "placeholder": "Enter your email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "title": "Valid email like user@example.com"
    })

    name = StringField("Full Name", validators=[DataRequired()],
        render_kw={"placeholder": "Enter your full name"})

    gender = SelectField("Gender", choices=[
        ('', 'Select'), ('m', 'Male'), ('f', 'Female'), ('o', 'Other')
    ], validators=[DataRequired()])

    address = TextAreaField("Address", validators=[DataRequired()],
        render_kw={"placeholder": "Enter address"})

    pincode = StringField("Pincode", validators=[
        DataRequired(), Regexp(r"^\d{6}$", message="Pincode must be 6 digits")
    ], render_kw={
        "pattern": r"\d{6}",
        "title": "Exactly 6 digit pincode"
    })

    phone = StringField("Phone", validators=[
        DataRequired(), Regexp(r"^[6-9]\d{9}$", message="Enter a valid 10-digit Indian phone number")
    ], render_kw={
        "pattern": r"[6-9]\d{9}",
        "title": "10-digit Indian number starting with 6–9"
    })

    password = PasswordField("Password", validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters")
    ], render_kw={
        "placeholder": "Enter password",
        "pattern": r".{6,}",
        "title": "Minimum 6 characters"
    })

    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ], render_kw={"placeholder": "Re-enter password"})

    submit = SubmitField("Register")

