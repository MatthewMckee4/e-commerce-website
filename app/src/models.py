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
    reviews = db.relationship("Review", back_populates="user")
    basket = db.relationship("Basket", uselist=False, back_populates="user")

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
    rating = db.Column(db.Float)

    seller_id = db.Column(db.Integer, db.ForeignKey("seller.id"), nullable=False)
    seller = db.relationship("Seller", back_populates="products")
    reviews = db.relationship("Review", back_populates="product")
    in_baskets = db.relationship("BasketItem", back_populates="product")

    def __repr__(self):
        return f"Product({self.id}, {self.name}, {self.price})"

    def has_user_reviewed(self, user):
        return any(review.user == user for review in self.reviews)

    def can_user_review(self, user):
        return not self.seller or user != self.seller.user


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    rating = db.Column(db.Integer)

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    product = db.relationship("Product", back_populates="reviews")
    user = db.relationship("User", back_populates="reviews")

    def __repr__(self):
        return f"Review({self.id}, Rating: {self.rating}, Product: {self.product.name}, User: {self.user.username})"


class Basket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="basket")

    items = db.relationship("BasketItem", back_populates="basket")

    def __repr__(self):
        return f"Basket({self.id}, User: {self.user.name}, {len(self.items)} Items)"


class BasketItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    basket_id = db.Column(db.Integer, db.ForeignKey("basket.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)  # Add this line

    product = db.relationship("Product", back_populates="in_baskets")
    basket = db.relationship("Basket", back_populates="items")

    def __repr__(self):
        return f"BasketItem(id: {self.id}, {self.product.name}, product_id: {self.product_id}, Qty: {self.quantity})"
