import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")  # konfigurowane w .env
ALGORITHM = "HS256"

# Ważność tokenów w minutach
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

user = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
uri = f"mongodb+srv://{user}:{password}@auctiondb.qc0xb7s.mongodb.net/?retryWrites=true&w=majority&appName=AuctionDB"

# MongoDB
MONGO_URL = uri
DB_NAME = os.getenv("DB_NAME", "auction_db")
