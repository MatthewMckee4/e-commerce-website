from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

from app.routes import login, users

app.register_blueprint(login.login_blueprint)
app.register_blueprint(users.users_blueprint)
