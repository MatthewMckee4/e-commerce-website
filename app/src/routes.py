from flask import render_template, url_for, flash, redirect, request
from src import app, db, bcrypt
from src.forms import (
    RegistrationForm,
    LoginForm,
    DeleteAccountForm,
    AccountForm,
    SellerForm,
    ProductForm,
    ReviewForm,
    DeleteReviewtForm,
)
from src.models import User, Product, Seller, Review
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/store", methods=["GET"])
def store():
    sort_option = request.args.get("sort")

    if sort_option == "name_asc":
        products = sorted(Product.query.all(), key=lambda x: x.name)
    elif sort_option == "name_desc":
        products = sorted(Product.query.all(), key=lambda x: x.name, reverse=True)
    elif sort_option == "price_asc":
        products = sorted(Product.query.all(), key=lambda x: x.price)
    elif sort_option == "price_desc":
        products = sorted(Product.query.all(), key=lambda x: x.price, reverse=True)
    else:
        products = sorted(Product.query.all(), key=lambda x: x.id)

    return render_template("store.html", products=products, sort_option=sort_option)


@app.route("/seller_account", methods=["GET", "POST"])
def seller_account():
    seller_form = SellerForm()
    product_form = ProductForm()
    if request.method == "POST":
        if seller_form.update.data and seller_form.validate_on_submit():
            user = User.query.get(current_user.id)
            # seller = Seller.query.get(current_user.id)
            if user:
                if seller_form.seller_name.data:
                    user.seller_info.name = seller_form.seller_name.data
                if seller_form.phone.data:
                    user.phone = seller_form.phone.data
                db.session.commit()

                flash("Seller Account details updated successfully", "success")

        if product_form.submit.data and product_form.validate_on_submit():
            image_url = save_uploaded_file(
                product_form.image_url.data, "product_images"
            )

            product = Product(
                name=product_form.name.data,
                description=product_form.description.data,
                price=product_form.price.data,
                image_url=image_url,
                quantity=product_form.quantity.data,
                seller_id=current_user.id,
            )
            db.session.add(product)
            db.session.commit()

            flash("Succesfully Added product", "success")

    return render_template(
        "seller_account.html",
        title="Seller Account",
        seller_form=seller_form,
        product_form=product_form,
        products=Product.query.all(),
    )


@app.route("/become_seller", methods=["GET", "POST"])
def become_seller():
    seller_form = SellerForm()

    if seller_form.validate_on_submit():
        seller = Seller(name=seller_form.seller_name.data, user_id=current_user.id)
        user = User.query.get(current_user.id)
        if user:
            user.phone = seller_form.phone.data
            user.is_seller = True
            db.session.add(seller)
            flash("Seller Account created successfully", "success")
        db.session.commit()

        return redirect(url_for("seller_account"))

    return render_template(
        "become_seller.html", title="Become A Seller", seller_form=seller_form
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in", "success")
        login_user(user, remember=True)
        return redirect(url_for("account"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email_username.data).first()

        if not user:
            user = User.query.filter_by(username=form.email_username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("account"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    delete_form = DeleteAccountForm()
    user = User.query.get(current_user.id)
    account_form = AccountForm(bio=user.bio)
    if request.method == "POST":
        if delete_form.confirm.data and delete_form.validate_on_submit():
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash("Your account has been deleted.", "success")
            return redirect(url_for("home"))

        if account_form.submit.data and account_form.validate_on_submit():
            if account_form.username.data or (
                not account_form.username.data and user.username
            ):
                user.username = account_form.username.data

            if account_form.first_name.data or (
                not account_form.first_name.data and user.first_name
            ):
                user.first_name = account_form.first_name.data

            if account_form.last_name.data or (
                not account_form.last_name.data and user.last_name
            ):
                user.last_name = account_form.last_name.data

            if account_form.email.data or (not account_form.email.data and user.email):
                user.email = account_form.email.data

            if account_form.bio.data or (not account_form.bio.data and user.bio):
                user.bio = account_form.bio.data

            if account_form.date_of_birth.data:
                user.date_of_birth = account_form.date_of_birth.data

            if account_form.logo.data:
                user.logo_url = save_uploaded_file(account_form.logo.data, "logos")

            db.session.commit()

            flash("Account details updated successfully", "success")

    return render_template(
        "account.html",
        title="Account",
        delete_form=delete_form,
        account_form=account_form,
    )


@app.route("/product/<int:product_id>", methods=["GET", "POST"])
def product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    review_form = ReviewForm()
    delete_review_form = DeleteReviewtForm()
    form = request.form.get("form")
    if request.method == "POST":
        if form == "post" and review_form.validate_on_submit():
            existing_review = Review.query.filter_by(
                product_id=product.id, user_id=current_user.id
            ).first()

            if existing_review:
                flash("You have already reviewed this product.", "error")
            else:
                review = Review(
                    text=review_form.text.data,
                    rating=review_form.rating.data,
                    product=product,
                    user=current_user,
                )
                db.session.add(review)
                db.session.commit()
                flash("Review posted successfully!", "success")
        elif form == "update" and review_form.validate_on_submit():
            existing_review = Review.query.filter_by(
                product_id=product.id, user_id=current_user.id
            ).first()

            if existing_review:
                if review_form.text.data or (
                    not review_form.text.data and existing_review.text
                ):
                    existing_review.text = review_form.text.data

                if review_form.rating.data or (
                    not review_form.rating.data and existing_review.rating
                ):
                    existing_review.rating = review_form.rating.data

                if not review_form.text.data and not review_form.rating.data:
                    db.session.delete(existing_review)
                    flash("Review deleted successfully.", "success")
                else:
                    flash("Review updated successfully!", "success")
                db.session.commit()
            else:
                flash("You have not reviewed this product yet.", "error")
        elif form == "delete" and delete_review_form.validate_on_submit():
            print("deleting review")
            review_to_delete = Review.query.get_or_404(
                delete_review_form.review_id.data
            )

            if review_to_delete.user == current_user:
                db.session.delete(review_to_delete)
                db.session.commit()
                flash("Review deleted successfully.", "success")
            else:
                flash("You are not authorized to delete this review.", "error")

    reviews = Review.query.filter_by(product_id=product.id).all()
    user_review = None
    for review in reviews:
        if review.user_id == current_user.id:
            user_review = review
            break

    average_rating = (
        db.session.query(func.avg(Review.rating))
        .filter_by(product_id=product_id)
        .scalar()
    )

    average_rating = round(average_rating, 1) if average_rating is not None else None

    return render_template(
        "product.html",
        title=product.name,
        product=product,
        review_form=review_form,
        delete_review_form=delete_review_form,
        user_review=user_review,
        average_rating=average_rating,
        seller=product.seller_id == current_user.seller_info.id,
    )


def save_uploaded_file(file_storage, directory):
    filename = secure_filename(file_storage.filename)
    file_path = os.path.join(app.root_path, "static", directory, filename)
    file_storage.save(file_path)
    return f"{directory}/{filename}"
