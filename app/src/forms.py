from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    DateField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from src.models import User
from flask_wtf.file import FileField, FileAllowed


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


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class LogoUploadForm(FlaskForm):
    logo = FileField("Upload Logo", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Upload")


class DeleteAccountForm(FlaskForm):
    confirm = SubmitField("Confirm Delete")
    submit = SubmitField("Delete Account")


class AccountForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    bio = TextAreaField("Bio")
    date_of_birth = DateField("Date of Birth", format="%Y-%m-%d")
    logo = FileField("Upload Logo", validators=[FileAllowed(["jpg", "png"])])
    submit = SubmitField("Save Changes")
