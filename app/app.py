from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/forgot")
def forgot_password():
    return render_template("forgot_password.html")


@app.route("/users", methods=["POST", "GET"])
def users():
    if request.method == "POST":
        user_name = request.form["name"]
        new_friend = User(name=user_name)

        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect("/users")
        except:
            return "There was an Error Adding the User"
    else:
        users = User.query.order_by(User.date_created)
        return render_template("users.html", users=users)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
