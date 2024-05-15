from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, url_for, request, redirect, session

import backend

app = Flask(__name__)
app.secret_key = "Halkd22f"
app.permanent_session_lifetime = timedelta(days=30)


@app.route("/")
def main():
    posts = backend.get_all_posts()
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
        if backend.register_user(username, password):
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
        if backend.login_user(username, password):
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
        backend.upload_message(session["user"], request.form["content"])
    return redirect(url_for("main"))


@app.route("/profile")
@check_login
def profile():
    username = session["user"]
    description = backend.get_description(username)
    posts = backend.get_user_posts(username)
    if posts == "TypeError":
        return render_template("index.html")
    return render_template("profile.html", username=username, posts=posts, description=description)


@app.route("/edit_profile", methods=["POST", "GET"])
@check_login
def edit_profile():
    if request.method == "GET":
        username = session["user"]
        description = backend.get_description(username)
        return render_template("edit_profile.html", username=username, description=description)
    if request.method == "POST":
        username_old = session["user"]
        username_new = request.form["new_name"]
        description = request.form["new_description"]
        if backend.edit_profile(username_old, username_new, description):
            session["user"] = username_new
        return redirect(url_for("main"))



@app.route("/post")
def user_post():
    post_id = request.args.get('post_id')
    if post_id is None:
        return "Post ID is missing!", 400
    post = backend.get_one_post(post_id)
    comments = post["comments"]
    return render_template("post.html", post=post, comments=comments)


@app.route("/likes/<post_id>")
@check_login
def likes(post_id):
    backend.update_likes(post_id, session["user"])
    return redirect(url_for("main"))


@app.route("/retweet/<post_id>")
@check_login
def retweet(post_id):
    backend.update_retweets(post_id, session["user"])
    return redirect(url_for("main"))


@app.route("/comment", methods=["POST"])
@check_login
def comment():
    backend.add_comment(request.form["post_id"], session["user"], request.form["comment_text"],
                        request.form["post_creator"])
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True, port=8020)
