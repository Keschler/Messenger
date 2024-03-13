from flask import Flask, render_template, url_for, request, redirect, session
from pymongo import MongoClient
from backend import register_user, login_user, get_all_posts, upload_message, update_likes, \
    update_retweets, get_user_posts
from datetime import timedelta
from functools import wraps

app = Flask(__name__)
app.secret_key = "5FGBisNot!mine"
app.permanent_session_lifetime = timedelta(days=30)


@app.route("/")
def main():
    posts = get_all_posts()
    if "user" in session:
        user = session["user"]
        return render_template("index.html", user=user, posts=posts)
    return render_template("index.html", posts=posts)


def check_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" in session:
            return f(*args, **kwargs)  # If user is logged in then execute the function
        else:
            return redirect(url_for("login"))

    return wrapper


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
            return render_template("register.html",
                                   error="The username is given or your username/password does not match the right pattern")
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
@check_login
def logout():
    session.pop("user", None)
    return redirect(url_for("main"))


@app.route("/post", methods=["POST"])
@check_login
def post():
    if request.form["content"]:
        upload_message(session["user"], request.form["content"])
    return redirect(url_for("main"))


@app.route("/profile")
@check_login
def profile():
    posts = get_user_posts(session["user"])
    return render_template("profile.html", username=session["user"], posts=posts)


@app.route("/likes/<post_id>")
@check_login
def likes(post_id):
    update_likes(post_id, session["user"])
    return redirect(session["last_page"])


@app.route("/retweet/<post_id>")
@check_login
def retweet(post_id):
    update_retweets(post_id, session["user"])
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True)
