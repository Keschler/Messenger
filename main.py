from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, url_for, request, redirect, session

from backend import User, Post

app = Flask(__name__)
app.secret_key = "Halkd22f"
app.permanent_session_lifetime = timedelta(days=30)


@app.route("/")
def main():
    posts = Post.get_all()
    if "user" in session:
        user = session["user"]
        return render_template("index.html", user=user, posts=posts, get_username=get_username)
    return render_template("index.html", posts=posts, get_username=get_username)


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
        user = User(username)
        if user.register(password):
            session.permanent = True
            session["user"] = username
            return redirect(url_for("main"))
        else:
            return render_template("register.html",
                                   error="The username is given or your username/password does not match the right "
                                         "pattern")
    elif request.method == "GET":
        if "user" in session:
            return redirect(url_for("main"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username)
        if user.login(password):
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


@app.route("/post")
def user_post():
    post_id = int(request.args.get('post_id'))
    if post_id is None:
        return "Post ID is missing!", 400
    post_instance = Post(post_id)
    post_details = post_instance.get_one()
    comments = post_details["comments"]
    return render_template("post.html", post=post_details, comments=comments)


@app.route("/post", methods=["POST"])
@check_login
def post():
    if request.form["content"]:
        Post.upload_message(session["user"], request.form["content"])
    return redirect(url_for("main"))


@app.route("/get_username/<user_id>")
def get_username(user_id):
    return User.get_username(user_id)


@app.route("/profile")
@check_login
def profile():
    username = session["user"]
    user = User(username)
    description = user.get_description()
    posts = Post.get_user(username)
    if posts == "TypeError":
        return render_template("index.html")
    return render_template("profile.html", username=username, posts=posts, description=description,
                           get_username=get_username)


@app.route("/edit_profile", methods=["POST", "GET"])
@check_login
def edit_profile():
    if request.method == "GET":
        username = session["user"]
        user = User(username)
        description = user.get_description()
        return render_template("edit_profile.html", username=username, description=description,
                               get_username=get_username)
    if request.method == "POST":
        username_old = session["user"]
        username_new = request.form["new_name"]
        description = request.form["new_description"]
        if not username_new.strip() and not description.strip():  # If both fields are empty
            return redirect(url_for("main"))
        user = User(username_old)
        if not username_new.strip():  # If description is empty
            user.edit_profile(username_old, description, False)
            return redirect(url_for("main"))
        if not description.strip():  # If name is empty
            user.edit_profile(username_new, description, None)
        else:
            user.edit_profile(username_new, description)
        session["user"] = username_new
        return redirect(url_for("main"))


@app.route("/likes/<post_id>")
@check_login
def likes(post_id):
    post_instance = Post(post_id)
    post_instance.update_likes(session["user"])
    return redirect(url_for("main"))


@app.route("/retweet/<post_id>")
@check_login
def retweet(post_id):
    post_instance = Post(post_id)
    post_instance.update_retweets(session["user"])
    return redirect(url_for("main"))


@app.route("/comment", methods=["POST"])
@check_login
def comment():
    post_instance = Post(int(request.form["post_id"]))
    post_instance.add_comment(session["user"], request.form["comment_text"],
                              request.form["post_creator"])
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(debug=True, port=8020)
