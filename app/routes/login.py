from flask import Blueprint, request, redirect, render_template
from app.models.user import User
from app import db

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login", methods=["POST", "GET"])
def login():
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
        return redirect("/")
