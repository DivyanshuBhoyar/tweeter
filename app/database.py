import motor.motor_asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient, TEXT
from dotenv import dotenv_values

config = dotenv_values('.env')

# client = MongoClient(config["MONGO_URI"], int(config["PORT"]))
# db = client["tweet-db"]


client = motor.motor_asyncio.AsyncIOMotorClient(config["MONGO_URI"])

db = client.tweet_db


# student_collection = db.get_collection("students_collection")
