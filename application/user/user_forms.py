from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Regexp, Length


class EditProfileForm(FlaskForm):
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

    email = StringField("Email", validators=[
        DataRequired(), Email(message="Invalid email"),
    ], render_kw={
        "placeholder": "Enter your email",
        "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "title": "Valid email like user@example.com"
    })


    avatar = FileField("Upload Profile Picture", validators=[
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], "Only image files are allowed")
        ])

    submit = SubmitField("Update Profile")

