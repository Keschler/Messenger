from flask import Flask, render_template, url_for, request, redirect, session
from pymongo import MongoClient
from backend import register_user, login_user, get_all_posts, upload_message
from datetime import timedelta
import logging


app = Flask(__name__)
app.secret_key = "5FGBisNot!mine"
app.permanent_session_lifetime = timedelta(days=30)
logging.basicConfig(level=logging.DEBUG)

@app.route("/")
def main():
    posts = get_all_posts()
    if "user" in session:
        user = session["user"]
        return render_template("index.html", user=user, posts=posts)
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if register_user(username, password):
            session.permanent = True
            session["user"] = username
            return redirect(url_for("main"))
        else:
            return render_template("register.html", error="The username is given or your username/password does not match the right pattern")
    elif request.method == "GET":
        if "user" in session:
            return redirect(url_for("main"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if login_user(username, password):
            session.permanent = True
            session["user"] = username
            return redirect(url_for("main"))
        else:
            return render_template("login.html", error="Wrong Password/Username")
    elif request.method == "GET":
        if "user" in session:
            return redirect(url_for("main"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("main"))

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/post", methods=["POST"])
def post():
    if "user" in session and request.form["content"]:
        upload_message(session["user"], request.form["content"])
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True)
