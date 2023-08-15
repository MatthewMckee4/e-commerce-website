from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, Flask World!"


@app.route("/create_table")
def create_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT)"""
    )
    conn.commit()
    conn.close()
    return "Table created successfully"


@app.route("/add_user/<username>")
def add_user(username):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()
    return f"User {username} added successfully"


@app.route("/users")
def list_users():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("users.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
