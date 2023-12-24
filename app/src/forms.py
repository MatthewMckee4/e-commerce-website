from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    DateField,
    FloatField,
    IntegerField,
    SelectField,
)
import re
from wtforms.validators import (
    DataRequired,
    Length,
    Email,
    ValidationError,
    Optional,
    NumberRange,
    Regexp,
)
from src.models import User
from flask_wtf.file import FileField, FileAllowed
from datetime import datetime


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
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

    def __init__(self, current_user, *args, **kwargs):
        super(AccountForm, self).__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_username(self, username):
        if username.data != self.current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    "That username is taken. Please choose a different one."
                )

    def validate_email(self, email):
        if email.data != self.current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    "That email is taken. Please choose a different one."
                )


class SellerForm(FlaskForm):
    seller_name = StringField("Seller Name", validators=[Length(min=2, max=20)])
    phone = StringField("Phone Number", validators=[Length(min=2, max=14)])
    submit = SubmitField("Become A Seller")
    update = SubmitField("Save Changes")

    def __init__(self, current_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_user = current_user

    def validate_phone(self, phone):
        if phone.data and (not phone.data.isdigit() or len(phone.data) > 15):
            raise ValidationError(
                "Invalid phone number. Please enter a valid phone number."
            )

        if (
            self.current_user.is_seller
            and self.phone.data == self.current_user.phone
            and self.update.data
        ):
            return

        existing_user_with_phone = User.query.filter_by(phone=phone.data).first()
        if existing_user_with_phone and existing_user_with_phone != self.current_user:
            raise ValidationError(
                "This phone number is already associated with another user."
            )


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(max=40)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired(), NumberRange(min=0)])
    image_url = FileField(
        "Upload Image", validators=[FileAllowed(["jpg", "png"]), DataRequired()]
    )
    quantity = IntegerField("Quantity", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Add Product")

    def validate_price(self, price):
        disallowed_symbols = ["$", "£", "€", "¥"]  # Add more symbols if needed
        if any(c in str(price.data) for c in disallowed_symbols):
            raise ValidationError("Price cannot contain currency symbols.")


class ReviewForm(FlaskForm):
    text = StringField("Add A Comment")
    rating = StringField(
        "Enter a Rating (0-100)",
        validators=[
            Length(min=0, max=3, message="Rating must be between 0 and 100."),
            Regexp("^(|[0-9]+)$", message="Rating must be a numeric value."),
        ],
        render_kw={"placeholder": "0-100"},
    )
    submit = SubmitField("Post Review")

    def validate_rating(self, rating):
        try:
            int_rating = int(float(rating.data))
            if int_rating != float(rating.data):
                raise ValidationError("Must be a Whole Number")
        except:
            pass
        else:
            if float(rating.data) > 100:
                raise ValidationError("Must be Less than or Equal to 100")


class DeleteReviewForm(FlaskForm):
    review_id = StringField("Review ID")
    submit = SubmitField("Delete")


class DeleteProductForm(FlaskForm):
    product_id = StringField("Product ID")
    submit = SubmitField("Delete")


class AddToBasketForm(FlaskForm):
    product_id = StringField("Product ID")
    quantity = SelectField(
        "Quantity:", choices=[(str(i), str(i)) for i in range(0, 31)], default="1"
    )
    submit = SubmitField("Add to Basket")

    def __repr__(self):
        return f"AddToBasketForm(product_id={self.product_id.data}, quantity={self.quantity.data})"
