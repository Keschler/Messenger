from pymongo import MongoClient
import bcrypt
import re
from datetime import datetime

cluster = MongoClient(
    "mongodb+srv://spadabailu:T94jkJaEAooyLhnhicmLhWTRVi3mu9X3WPDxWfDfWACcKjMeWs@cluster0.fzgybta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["twitter"]


def register_user(username, password):
    if not input_validation(username):
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
    if not input_validation(username):
        return False
    user_info = db["users"].find_one({"username": username})
    if user_info and bcrypt.checkpw(password.encode("utf-8"), user_info["password"]):
        return True
    else:
        return False


def get_all_posts():
    posts = db["posts"].find().sort("_id", -1)
    return list(posts)


def get_user_posts(username):
    user_posts = db["users"].find_one({"username": username})["posts"]  # Get the posts of the user
    reversed_user_posts = user_posts[::-1]  # Reverse the list to show the latest post first
    return reversed_user_posts


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
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "retweets": 0,
        "liked_by": [],
        "retweeted_by": [],
        "comments": []
    }
    db["posts"].insert_one(post)  # Insert the post into the database
    db["users"].update_one({"username": user}, {"$push": {"posts": post}})
    return None


def add_comment(post_id, username, content):
    db["posts"].update_one({"_id": int(post_id)}, {"$push": {"comments": {"user": username, "content": content,
                                                                          "date": datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S")}}})
    return None


def update_likes(post_id, username):
    int_post_id = int(post_id)
    # Find the post to see if the user has liked it
    post = db["posts"].find_one({"_id": int_post_id})

    if post is None:
        return "Post not found."
    print(post)
    # If the user has not liked the post
    if username not in post.get("liked_by", []):
        print("not liked")
        db["posts"].update_one({"_id": int_post_id}, {"$inc": {"likes": 1}, "$push": {"liked_by": username}})
        db["users"].update_one({"username": username, "posts._id": int_post_id},
                               {"$inc": {"posts.$.likes": 1}, "$push": {"liked_posts": int_post_id}})
    else:
        db["posts"].update_one({"_id": int_post_id}, {"$inc": {"likes": -1}, "$pull": {"liked_by": username}})
        db["users"].update_one({"username": username, "posts._id": int_post_id},
                               {"$inc": {"posts.$.likes": -1}, "$pull": {"liked_posts": int_post_id}})
    return None


def update_retweets(post_id, username):
    int_post_id = int(post_id)
    post = db["posts"].find_one({"_id": int_post_id})

    if post is None:
        return "Post not found."

    if username not in post.get("retweeted_by", []):
        db["posts"].update_one({"_id": int_post_id}, {"$inc": {"retweets": 1}, "$push": {"retweeted_by": username}})
        # We need to ensure we are incrementing retweets for the specific post in the user's posts array.
        db["users"].update_one(
            {"username": username, "posts._id": int_post_id},
            {"$inc": {"posts.$.retweets": 1}, "$push": {"retweeted_posts": int_post_id}}
        )
    else:
        db["posts"].update_one({"_id": int_post_id}, {"$inc": {"retweets": -1}, "$pull": {"retweeted_by": username}})
        # Likewise, decrementing retweets for the specific post in the user's posts array.
        db["users"].update_one(
            {"username": username, "posts._id": int_post_id},
            {"$inc": {"posts.$.retweets": -1}, "$pull": {"retweeted_posts": int_post_id}}
        )
    return None


def add_comment(post_id, username, content):
    db["posts"].update_one({"_id": int(post_id)}, {"$push": {"comments": {"user": username, "content": content,
                                                                          "date": datetime.now().strftime(
                                                                              "%Y-%m-%d %H:%M:%S")}}})
    return None
