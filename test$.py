import pymongo
from pymongo import MongoClient


cluster = MongoClient(
    "mongodb+srv://spadabailu:T94jkJaEAooyLhnhicmLhWTRVi3mu9X3WPDxWfDfWACcKjMeWs@cluster0.fzgybta.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = cluster["twitter"]
collection = db["posts"]

post = {"_id": 2, "user": "yunfan", "content": "Big fish"}

output = db["users"].find_one({"username": "yunfan"})
print(output["password"])
