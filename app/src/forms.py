from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    DateField,
)
import re
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
    Optional,
)
from src.models import User
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")

    def validate_password(self, password):
        if len(password.data) < 7:
            raise ValidationError("Password must be at least 7 characters long.")

        if not re.search(r"[A-Z]", password.data):
            raise ValidationError("Password must contain at least one capital letter.")

        if not re.search(r"[a-z]", password.data):
            raise ValidationError(
                "Password must contain at least one lowercase letter."
            )

        if not re.search(r"\d", password.data):
            raise ValidationError("Password must contain at least one digit.")

        if not re.search(r"[._!-]", password.data):
            raise ValidationError(
                "Password must contain at least one special character (._-!)."
            )


class LoginForm(FlaskForm):
    email_username = StringField("Email or Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class DeleteAccountForm(FlaskForm):
    confirm = SubmitField("Confirm Delete")
    submit = SubmitField("Delete Account")


class CustomDateField(DateField):
    def process_formdata(self, valuelist):
        if valuelist:
            date_string = valuelist[0]
            try:
                self.data = datetime.strptime(date_string, self.format[0]).date()
            except (ValueError, IndexError):
                self.data = None
        else:
            self.data = None


class AccountForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=2, max=20)])
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    email = StringField("Email", validators=[Email()])
    bio = TextAreaField("Bio")
    date_of_birth = CustomDateField(
        "Date of Birth", format="%Y-%m-%d", validators=[Optional()]
    )
    logo = FileField("Upload Logo", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Save Changes")
