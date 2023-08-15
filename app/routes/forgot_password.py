from flask import render_template
from app.main import app


@app.route("/forgot")
def forgot_password():
    return render_template("forgot_password.html")
