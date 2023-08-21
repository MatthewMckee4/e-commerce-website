from flask import render_template, url_for, flash, redirect, request, jsonify
from src import app, db, bcrypt
from src.forms import (
    RegistrationForm,
    LoginForm,
    DeleteAccountForm,
    AccountForm,
    SellerForm,
    ProductForm,
    ReviewForm,
    DeleteReviewForm,
    DeleteProductForm,
    AddToBasketForm,
)
from src.models import User, Product, Seller, Review, Basket, BasketItem
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func


def get_basket_items(user_basket):
    return BasketItem.query.filter_by(basket_id=user_basket.id).all()


def calculate_basket_total(basket_items):
    return round(sum(item.product.price * item.quantity for item in basket_items), 2)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title="Home")


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/basket", methods=["GET", "POST"])
def basket():
    if current_user.is_authenticated:
        user_basket = Basket.query.filter_by(user_id=current_user.id).first()

        if user_basket:
            basket_items = get_basket_items(user_basket)
            form_dict = {}  # To store forms for each item

            for item in basket_items:
                form = AddToBasketForm()
                form_dict[item.id] = form

            if request.method == "POST":
                item_id = int(request.form.get("product_id"))

                basket_item = BasketItem.query.filter_by(id=item_id).first()
                new_quantity = form_dict[item_id].quantity.data
                if int(new_quantity) == 0:
                    print(basket_item)
                    db.session.delete(basket_item)
                else:
                    basket_item.quantity = int(new_quantity)
                db.session.commit()

            for item in basket_items:
                form_dict[item.id].quantity.data = str(item.quantity)

            # Refresh basket items and total after potential updates
            basket_items = get_basket_items(user_basket)
            basket_total = calculate_basket_total(basket_items)

            return render_template(
                "basket.html",
                title="Basket",
                user_basket=user_basket,
                basket_items=basket_items,
                basket_total=basket_total,
                form_dict=form_dict,
            )

        else:
            return render_template("basket.html", title="Basket")

    else:
        flash("Please log in to view your basket.", "info")
        return redirect(url_for("login"))  # Redirect to login page

    return render_template("basket.html", title="Basket")


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
    seller_form = SellerForm(current_user=current_user)
    product_form = ProductForm()
    delete_product_form = DeleteProductForm()
    form = request.form.get("form")

    if request.method == "POST":
        if form == "seller" and seller_form.validate_on_submit():
            user = User.query.get(current_user.id)
            # seller = Seller.query.get(current_user.id)
            if user:
                if seller_form.seller_name.data:
                    user.seller_info.name = seller_form.seller_name.data
                if seller_form.phone.data:
                    user.phone = seller_form.phone.data
                db.session.commit()

                flash("Seller Account details updated successfully", "success")

        elif form == "product" and product_form.validate_on_submit():
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

        elif form == "delete" and delete_product_form.validate_on_submit():
            product_id_to_delete = delete_product_form.product_id.data
            product_to_delete = Product.query.get(product_id_to_delete)
            if product_to_delete and product_to_delete.seller_id == current_user.id:
                db.session.delete(product_to_delete)
                db.session.commit()
                flash("Product deleted successfully", "success")
            else:
                flash("You are not authorized to delete this product", "danger")

    return render_template(
        "seller_account.html",
        title="Seller Account",
        seller_form=seller_form,
        product_form=product_form,
        delete_product_form=delete_product_form,
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
    account_form = AccountForm(current_user=current_user)
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
    delete_review_form = DeleteReviewForm()
    add_to_basket_form = AddToBasketForm()

    def add_review():
        try:
            if not current_user.is_authenticated:
                flash("You need to be logged in to post a review.", "error")
                return redirect(url_for("login"))  # Redirect to login page

            if not review_form.validate_on_submit():
                flash("Invalid review submission.", "error")
                return redirect(request.referrer or url_for("index"))  # Redirect back

            existing_review = Review.query.filter_by(
                product_id=product.id, user_id=current_user.id
            ).first()

            if existing_review:
                flash("You have already reviewed this product.", "error")
                return redirect(
                    request.referrer or url_for("product_detail", product_id=product.id)
                )

            review = Review(
                text=review_form.text.data,
                rating=review_form.rating.data,
                product=product,
                user=current_user,
            )
            db.session.add(review)
            db.session.commit()
            flash("Review posted successfully!", "success")
            return redirect(url_for("product", product_id=product.id))

        except Exception as e:
            flash("An error occurred while posting your review.", "error")
            # Log the error for debugging purposes
            print(e)
            return redirect(request.referrer or url_for("index"))  # Redirect back

    def update_review():
        try:
            if not current_user.is_authenticated:
                flash("You need to be logged in to update a review.", "error")
                return redirect(url_for("login"))  # Redirect to login page

            if not review_form.validate_on_submit():
                flash("Invalid review update.", "error")
                return redirect(request.referrer or url_for("index"))  # Redirect back

            existing_review = Review.query.filter_by(
                product_id=product.id, user_id=current_user.id
            ).first()

            if existing_review:
                if review_form.text.data or existing_review.text:
                    existing_review.text = review_form.text.data

                if review_form.rating.data or existing_review.rating:
                    existing_review.rating = review_form.rating.data

                if not review_form.text.data and not review_form.rating.data:
                    db.session.delete(existing_review)
                    flash("Review deleted successfully.", "success")
                else:
                    flash("Review updated successfully!", "success")
                db.session.commit()
            else:
                flash("You have not reviewed this product yet.", "error")

            return redirect(url_for("product", product_id=product.id))

        except Exception as e:
            flash("An error occurred while updating your review.", "error")
            # Log the error for debugging purposes
            print(e)
            return redirect(request.referrer or url_for("index"))  # Redirect back

    def delete_review():
        try:
            if not current_user.is_authenticated:
                flash("You need to be logged in to delete a review.", "error")
                return redirect(url_for("login"))  # Redirect to login page

            if not delete_review_form.validate_on_submit():
                flash("Invalid request to delete a review.", "error")
                return redirect(request.referrer or url_for("index"))  # Redirect back

            review_to_delete = Review.query.get_or_404(
                delete_review_form.review_id.data
            )

            if review_to_delete.user == current_user:
                db.session.delete(review_to_delete)
                db.session.commit()
                flash("Review deleted successfully.", "success")
            else:
                flash("You are not authorized to delete this review.", "error")

            return redirect(url_for("product", product_id=review_to_delete.product_id))

        except Exception as e:
            flash("An error occurred while deleting the review.", "error")
            # Log the error for debugging purposes
            print(e)
            return redirect(request.referrer or url_for("index"))  # Redirect back

    def add_to_basket():
        try:
            if not current_user.is_authenticated:
                flash("You need to be logged in to add items to your basket.", "error")
                return redirect(url_for("login"))  # Redirect to login page

            if not add_to_basket_form.validate_on_submit():
                flash("Invalid quantity value.", "error")
                return redirect(request.referrer or url_for("index"))  # Redirect back

            product = Product.query.get_or_404(product_id)
            user_basket = current_user.basket

            if user_basket is None:
                user_basket = Basket(user=current_user)
                db.session.add(user_basket)
                db.session.commit()

            basket_item = BasketItem.query.filter_by(
                basket=user_basket, product=product
            ).first()
            if basket_item:
                basket_item.quantity += int(add_to_basket_form.quantity.data)
            else:
                basket_item = BasketItem(
                    basket=user_basket,
                    product=product,
                    quantity=int(add_to_basket_form.quantity.data),
                )
                db.session.add(basket_item)
            db.session.commit()

            flash(f"{product.name} added to your basket!", "success")
            return redirect(url_for("basket"))

        except Exception as e:
            flash("An error occurred while adding to your basket.", "error")
            # Log the error for debugging purposes
            print(e)
            return redirect(request.referrer or url_for("index"))  # Redirect back

    if request.method == "POST":
        form_handlers = {
            "post": add_review,
            "update": update_review,
            "delete": delete_review,
            "basket": add_to_basket,
        }

        form = request.form.get("form")
        if form in form_handlers:
            form_handlers[form]()

    user_review = next(
        (review for review in product.reviews if review.user_id == current_user.id),
        None,
    )

    average_rating = (
        db.session.query(func.avg(Review.rating))
        .filter_by(product_id=product_id)
        .scalar()
    )

    average_rating = round(average_rating, 0) if average_rating is not None else None

    return render_template(
        "product.html",
        title=product.name,
        product=product,
        review_form=review_form,
        delete_review_form=delete_review_form,
        add_to_basket_form=add_to_basket_form,
        user_review=user_review,
        average_rating=average_rating,
        seller=product.seller_id == current_user.seller_info.id,
    )


def save_uploaded_file(file_storage, directory):
    filename = secure_filename(file_storage.filename)
    file_path = os.path.join(app.root_path, "static", directory, filename)
    file_storage.save(file_path)
    return f"{directory}/{filename}"
