import re
from datetime import datetime

import bcrypt
from pymongo import MongoClient

cluster = MongoClient(
    "mongodb+srv://spadabailu:T94jkJaEAooyLhnhicmLhWTRVi3mu9X3WPDxWfDfWACcKjMeWs@cluster0.fzgybta.mongodb.net"
    "/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["twitter"]


def input_validation(username: str):
    username_pattern = re.compile("^[a-zA-Z0-9]+$")
    if username_pattern.match(username):
        return True
    else:
        return False


class User:
    def __init__(self, username: str):
        self.username = username

    def register(self, password: str):
        description = ''
        if not input_validation(self.username):
            return False
        if db["users"].find_one({"username": self.username}) is None:  # If there is no user with the same name
            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt())
            db["users"].insert_one({"_id": db["users"].count_documents(
                {}) + 1, "username": self.username, "password": hashed_password, "description": description,
                                    "posts": [],
                                    "liked_posts": [],
                                    "retweeted_posts": []})
            return True
        else:
            return False

    def login(self, password: str):
        if not input_validation(self.username):
            return False
        user_info = db["users"].find_one({"username": self.username})
        if user_info and bcrypt.checkpw(password.encode("utf-8"), user_info["password"]):
            return True
        else:
            return False

    def get_description(self):
        try:
            description = db["users"].find_one({"username": self.username})["description"]
        except TypeError:
            return "TypeError"
        return description

    @staticmethod
    def get_username(id):
        username = db["users"].find_one({"_id": id})["username"]
        return username

    def edit_profile(self, username_new: str, description: str):
        if db["users"].find_one({"username": username_new}) is None:
            db["users"].update_one({"username": self.username},
                                   {"$set": {"description": description, "username": username_new}})
            return True
        return False


class Post:
    def __init__(self, post_id: int = None):
        self.post_id = post_id

    @staticmethod
    def get_all():
        posts = db["posts"].find().sort("_id", -1)
        return list(posts)

    def get_one(self):
        try:
            user_posts = db["posts"].find_one({"_id": int(self.post_id)})
        except TypeError:
            return "TypeError"
        return user_posts

    @staticmethod
    def get_user(username: str):
        try:
            user_posts = db["users"].find_one({"username": username})["posts"]
        except TypeError:
            return "TypeError"
        reversed_user_posts = user_posts[::-1]  # Reverse the list to show the latest post first
        return reversed_user_posts

    @staticmethod
    def upload_message(username: str, content: str):
        user_id = db["users"].find_one({"username": username})["_id"]
        post = {
            "_id": db["posts"].count_documents({}) + 1,
            "user_id": user_id,
            "content": content,
            "likes": 0,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "retweets": 0,
            "liked_by": [],
            "retweeted_by": [],
            "comments": []
        }
        db["posts"].insert_one(post)
        db["users"].update_one({"username": username}, {"$push": {"posts": post}})
        return None

    def add_comment(self, username: str, content: str, post_creator: str):
        print(self.post_id, username, content, post_creator)
        int_post_id = int(self.post_id)
        comment = {"comments": {"user": username, "content": content,
                                "date": datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")}}
        db["posts"].update_one({"_id": int_post_id}, {"$push": comment})
        db["users"].update_one({"username": post_creator, "posts._id": int_post_id},
                               {"$push": {"posts.$.comments": comment}})

    def update_likes(self, username: str):
        int_post_id = int(self.post_id)
        post = db["posts"].find_one({"_id": int_post_id})

        if post is None:
            return "Post not found."
        if username not in post.get("liked_by", []):
            db["posts"].update_one({"_id": int_post_id}, {"$inc": {"likes": 1}, "$push": {"liked_by": username}})
            db["users"].update_one({"username": username, "posts._id": int_post_id},
                                   {"$inc": {"posts.$.likes": 1}, "$push": {"liked_posts": int_post_id}})
        else:
            db["posts"].update_one({"_id": int_post_id}, {"$inc": {"likes": -1}, "$pull": {"liked_by": username}})
            db["users"].update_one({"username": username, "posts._id": int_post_id},
                                   {"$inc": {"posts.$.likes": -1}, "$pull": {"liked_posts": int_post_id}})
        return None

    def update_retweets(self, username):
        int_post_id = int(self.post_id)
        post = db["posts"].find_one({"_id": int_post_id})

        if post is None:
            return "Post not found."

        if username not in post.get("retweeted_by", []):
            db["posts"].update_one({"_id": int_post_id}, {"$inc": {"retweets": 1}, "$push": {"retweeted_by": username}})
            db["users"].update_one(
                {"username": username, "posts._id": int_post_id},
                {"$inc": {"posts.$.retweets": 1}, "$push": {"retweeted_posts": int_post_id}}
            )
        else:
            db["posts"].update_one({"_id": int_post_id},
                                   {"$inc": {"retweets": -1}, "$pull": {"retweeted_by": username}})
            db["users"].update_one(
                {"username": username, "posts._id": int_post_id},
                {"$inc": {"posts.$.retweets": -1}, "$pull": {"retweeted_posts": int_post_id}}
            )
        return None
