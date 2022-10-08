from pymongo import MongoClient, TEXT
from dotenv import dotenv_values

config = dotenv_values('.env')

client = MongoClient(config["MONGO_URI"], int(config["PORT"]))
db = client["tweet-db"]
