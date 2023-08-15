from flask import Blueprint, request, redirect, render_template
from app.models.user import User
from app import db

users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/users", methods=["POST", "GET"])
def users():
    if request.method == "POST":
        user_name = request.form["name"]
        new_user = User(name=user_name)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect("/users")
        except:
            return "There was an Error Adding the User"
    else:
        users = User.query.order_by(User.date_created)
        return render_template("templates/users.html", users=users)
