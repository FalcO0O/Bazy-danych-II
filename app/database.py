import motor.motor_asyncio
from config import MONGO_URL, DB_NAME

# Inicjalizujemy asynchronicznego klienta Motor
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

# Wskazujemy konkretną bazę
db = client[DB_NAME]

# Kolekcje
users_collection = db["users"]              # Kolekcja users
auctions_collection = db["auction"]         # Kolekcja aukcji
bids_collection = db["auction.bids"]        # Kolekcja ofert (bids)
history_collection = db["auction.history"]  # Kolekcja zakończonych aukcji (history)
logs_collection = db["log"]                 # Kolekcja logów operacji

def get_client():
    return client