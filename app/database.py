from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo_db:27017")
client = AsyncIOMotorClient(MONGO_URL)
db = client["auction_db"]

users_collection = db["users"]
logs_collection = db["logs"] 