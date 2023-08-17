from datetime import datetime
from src import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    logo_url = db.Column(db.String(255), default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    is_seller = db.Column(db.Boolean, default=False)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    bio = db.Column(db.String(500))
    date_of_birth = db.Column(db.Date)

    phone = db.Column(db.String(20))

    seller_info = db.relationship("Seller", uselist=False, back_populates="user")
    comments = db.relationship("Comment", back_populates="user")

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email})"


class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="seller_info")

    products = db.relationship("Product", back_populates="seller")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), default="default_product.jpg")
    quantity = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey("seller.id"), nullable=False)
    rating = db.Column(db.Float)

    seller = db.relationship("Seller", back_populates="products")
    comments = db.relationship("Comment", back_populates="product")

    def __repr__(self):
        return f"Product({self.id}, {self.name}, {self.price})"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    product = db.relationship("Product", back_populates="comments")
    user = db.relationship("User", back_populates="comments")
