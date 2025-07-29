from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Email, Regexp, Length, NumberRange


class EditProfileForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()],
        render_kw={"placeholder": "Enter your full name"})

    gender = SelectField("Gender", choices=[
        ('', 'Select'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')
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

    email = StringField("Email", validators=[
        DataRequired(), Email(message="Invalid email"),
    ], render_kw={
        "placeholder": "Enter your email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "title": "Valid email like user@example.com"
    })


    avatar = FileField("Upload Profile Picture", validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Only image files are allowed")
        ], render_kw={
        "title": "Select your profile picture"
    })

    submit = SubmitField("Update Profile")


class LotForm(FlaskForm):
    name = StringField("Lot Name", validators=[
        DataRequired(),
        Length(min=2, max=60)
    ], render_kw={
        "placeholder": "Lot Name",
        "title": "Enter the lot name",
        "pattern": r"^[a-zA-Z]+[a-zA-Z0-9_- ]+$"
    })
    cost_per_hour = DecimalField("Cost per Hour (₹)", places=2, validators=[
        DataRequired(),
        NumberRange(min=0, max=1000)
    ], render_kw={
        "placeholder": "100",
        "title": "Enter the cost per hour",
        "pattern": r"^[0-9]{1,3}$"
    })
    address = StringField("Address", validators=[
        DataRequired(),
        Length(min=5, max=255)
    ], render_kw={
        "placeholder": "Lot Address",
        "title": "Enter the address",
        "pattern": r"^[a-zA-Z]+[a-zA-Z0-9_- ]+$"
    })
    pincode = StringField("Pincode", validators=[
        DataRequired(),
        Length(min=6, max=6, message="Pincode must be exactly 6 digits")
    ], render_kw={
        "pattern": r"^\d{6}$",
        "title": "Enter the pincode",
        "placeholder": "XXXXXX"
    })
    max_spots = IntegerField("Max Parking Spots", validators=[
        DataRequired(),
        NumberRange(min=1, max=1000)
    ], render_kw={
        "placeholder": "100",
        "title": "Enter the max parking spots",
        "pattern": r"^[0-9]{1,3}$"
    })

    submit = SubmitField("Submit")