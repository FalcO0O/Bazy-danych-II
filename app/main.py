from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(mongo_url)
db = client.mydatabase

@app.get("/")
def read_root():
    return {"message": "MongoDB is connected", "collections": db.list_collection_names()}
