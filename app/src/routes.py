from flask import render_template, url_for, flash, redirect, request
from src import app, db, bcrypt
from src.forms import RegistrationForm, LoginForm, LogoUploadForm, DeleteAccountForm
from src.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

posts = [
    {
        "author": "Matthew Mckee",
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": "April 20, 2018",
    },
    {
        "author": "Matthew Mckee",
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": "April 21, 2018",
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


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
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    logo_form = LogoUploadForm()
    delete_form = DeleteAccountForm()

    if logo_form.validate_on_submit():
        if logo_form.logo.data:
            logo_filename = secure_filename(logo_form.logo.data.filename)
            logo_path = os.path.join(app.root_path, "static", "logos", logo_filename)
            logo_form.logo.data.save(logo_path)
            current_user.logo_url = f"logos/{logo_filename}"
            db.session.commit()
            flash("Logo uploaded successfully!", "success")

    if delete_form.validate_on_submit():
        if request.method == "POST":
            db.session.delete(current_user)  # Delete user from the database
            db.session.commit()
            logout_user()  # Log the user out
            flash("Your account has been deleted.", "success")
            return redirect(url_for("home"))

    return render_template(
        "account.html", title="Account", logo_form=logo_form, delete_form=delete_form
    )
