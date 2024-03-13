from pymongo import MongoClient
import bcrypt
import re
import datetime

cluster = MongoClient(
    "mongodb+srv://spadabailu:T94jkJaEAooyLhnhicmLhWTRVi3mu9X3WPDxWfDfWACcKjMeWs@cluster0.fzgybta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["twitter"]


def register_user(username, password):
    if not input_validation(username, password):
        return False
    if db["users"].find_one({"username": username}) is None:  # If there is no user with the same name
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
        db["users"].insert_one({"_id": db["users"].count_documents(
            {}) + 1, "username": username, "password": hashed_password, "posts": [], "liked_posts": [],
                                "retweeted_posts": []})
        return True
    else:
        return False


def login_user(username, password):
    if not input_validation(username, password):
        return False
    user_info = db["users"].find_one({"username": username})
    if user_info and bcrypt.checkpw(password.encode("utf-8"), user_info["password"]):
        return True
    else:
        return False


def get_all_posts():
    posts = db["posts"].find()
    return list(posts)


def get_user_posts(username):
    user_posts = db["users"].find_one({"username": username})["posts"] # Get the posts of the user
    return user_posts


def input_validation(username):
    username_pattern = re.compile("^[a-zA-Z0-9]+$")
    if username_pattern.match(username):
        return True
    else:
        return False


def upload_message(user, content):
    post = {
        "_id": db["posts"].count_documents({}) + 1,
        "user": user,
        "content": content,
        "likes": 0,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "retweets": 0,
        "liked_by": [],
        "retweeted_by": []
    }
    db["posts"].insert_one(post)  # Insert the post into the database
    db["users"].update_one({"username": user}, {"$push": {"posts": post}})
    return None


def update_likes(post_id, username):
    if username not in db["posts"].find_one({"_id": int(post_id)})["liked_by"]:  # If the user has not liked the post
        db["posts"].update_one({"_id": int(post_id)}, {"$inc": {"likes": 1}, "$push": {"liked_by": username}})
        db["users"].update_one({"username": username}, {"$push": {"liked_posts": int(post_id)}})
    else:
        db["posts"].update_one({"_id": int(post_id)}, {"$inc": {"likes": -1}, "$pull": {"liked_by": username}})
        db["users"].update_one({"username": username}, {"$pull": {"liked_posts": int(post_id)}})
    return None


def update_retweets(post_id, username):
    if username not in db["posts"].find_one({"_id": int(post_id)})[
        "retweeted_by"]:  # If the user has not retweeted the post
        db["posts"].update_one({"_id": int(post_id)}, {"$inc": {"retweets": 1}, "$push": {"retweeted_by": username}})
        db["users"].update_one({"username": username}, {"$push": {"retweeted_posts": int(post_id)}})
    else:
        db["posts"].update_one({"_id": int(post_id)}, {"$inc": {"retweets": -1}, "$pull": {"retweeted_by": username}})
        db["users"].update_one({"username": username}, {"$pull": {"retweeted_posts": int(post_id)}})
    return None
