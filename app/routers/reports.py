from fastapi import APIRouter, Depends
from database import history_collection, auctions_collection
from schemas import AuctionHistoryOut
from typing import List
from dependencies import get_current_admin
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/reports",
    tags=["reports"]
)

@router.get("/history", response_model=List[AuctionHistoryOut])
async def auctions_history(admin: dict = Depends(get_current_admin)):
    """
    Pobranie historii wszystkich aukcji (dla administratora).
    """
    cursor = history_collection.find()
    history_list = []
    async for doc in cursor:
        history_list.append(AuctionHistoryOut(
            id=str(doc["_id"]),
            title=doc["title"],
            description=doc.get("description"),
            owner_id=doc["owner_id"],
            created_at=doc["created_at"],
            closed_at=doc["closed_at"],
            winner_id=doc.get("winner_id"),
            final_price=doc.get("final_price")
        ))
    return history_list

@router.get("/user-spending")
async def get_user_spending(admin: dict = Depends(get_current_admin)):
    """
    Pobranie sumy wydatków każdego użytkownika, który wygrał przynajmniej jedną aukcję.
    Widoczne tylko dla administratora.
    """
    pipeline = [
        {"$match": {"winner_id": {"$ne": None}}},
        {"$group": {
            "_id": "$winner_id",
            "total_spent": {"$sum": "$final_price"},
            "won_count": {"$sum": 1}
        }},
        {"$addFields": {"user_obj_id": {"$toObjectId": "$_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "user_obj_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": "$user"},
        {"$project": {
            "user_id": "$_id",
            "username": "$user.username",
            "email": "$user.email",
            "total_spent": 1,
            "won_count": 1
        }},
        {"$sort": {"total_spent": -1}}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/top-winners")
async def top_winners(limit: int = 10, admin: dict = Depends(get_current_admin)):
    """
    Pobranie listy użytkowników z największą liczbą wygranych aukcji (domyślnie top 10).
    Widoczne tylko dla administratora.
    """
    pipeline = [
        {"$match": {"winner_id": {"$ne": None}}},
        {"$group": {
            "_id": "$winner_id",
            "won_count": {"$sum": 1},
            "total_spent": {"$sum": "$final_price"}
        }},
        {"$addFields": {"user_obj_id": {"$toObjectId": "$_id"}}},
        {"$lookup": {
            "from": "users",
            "localField": "user_obj_id",
            "foreignField": "_id",
            "as": "user"
        }},
        {"$unwind": "$user"},
        {"$project": {
            "user_id": "$_id",
            "username": "$user.username",
            "won_count": 1,
            "total_spent": 1
        }},
        {"$sort": {"won_count": -1}},
        {"$limit": limit}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/total-cashflow")
async def total_cashflow(admin: dict = Depends(get_current_admin)):
    """
    Pobranie całkowitej wartości pieniężnej wygenerowanej przez zakończone aukcje.
    Dostępne tylko dla administratora.
    """
    result = await history_collection.aggregate([
        {"$match": {"winner_id": {"$ne": None}}},
        {"$group": {"_id": None, "total": {"$sum": "$final_price"}}}
    ]).to_list(length=1)
    return {"total_cashflow": result[0]["total"] if result else 0}

@router.get("/high-value-auctions")
async def high_value_auctions(min_price: float = 1000.0, admin: dict = Depends(get_current_admin)):
    """
    Pobranie aukcji, których cena końcowa przekroczyła określoną wartość minimalną (domyślnie 1000).
    Widoczne tylko dla administratora.
    """
    pipeline = [
        {"$match": {"final_price": {"$gte": min_price}}},
        {"$project": {
            "id": {"$toString": "$_id"},
            "title": 1,
            "description": 1,
            "owner_id": 1,
            "created_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$created_at"}},
            "closed_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$closed_at"}},
            "winner_id": 1,
            "final_price": 1,
            "_id": 0
        }}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/last-week-auctions")
async def last_week_auctions(admin: dict = Depends(get_current_admin)):
    """
    Pobranie aukcji utworzonych w ciągu ostatnich 7 dni.
    Widoczne tylko dla administratora.
    """
    since = datetime.now(timezone.utc) - timedelta(days=7)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$project": {
            "id": {"$toString": "$_id"},
            "title": 1,
            "description": 1,
            "owner_id": 1,
            "created_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$created_at"}},
            "closed_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$closed_at"}},
            "winner_id": 1,
            "final_price": 1,
            "_id": 0
        }}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/last-month-auctions")
async def last_month_auctions(admin: dict = Depends(get_current_admin)):
    """
    Pobranie aukcji utworzonych w ciągu ostatnich 30 dni.
    Widoczne tylko dla administratora.
    """
    since = datetime.now(timezone.utc) - timedelta(days=30)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$project": {
            "id": {"$toString": "$_id"},
            "title": 1,
            "description": 1,
            "owner_id": 1,
            "created_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$created_at"}},
            "closed_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$closed_at"}},
            "winner_id": 1,
            "final_price": 1,
            "_id": 0
        }}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/last-6h-auctions")
async def last_6h_auctions(admin: dict = Depends(get_current_admin)):
    """
    Pobranie aukcji utworzonych w ciągu ostatnich 6 godzin.
    Widoczne tylko dla administratora.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=6)
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$project": {
            "id": {"$toString": "$_id"},
            "title": 1,
            "description": 1,
            "owner_id": 1,
            "created_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$created_at"}},
            "closed_at": {"$dateToString": {"format": "%Y-%m-%dT%H:%M:%S%z", "date": "$closed_at"}},
            "winner_id": 1,
            "final_price": 1,
            "_id": 0
        }}
    ]
    results = await history_collection.aggregate(pipeline).to_list(length=None)
    return results

@router.get("/auctions-stats")

async def auctions_stats(admin: dict = Depends(get_current_admin)):
    """
    Pobranie statystyk aukcji: liczba aktywnych i zamkniętych aukcji.
    Widoczne tylko dla administratora.
    """
    auctions_active_count = await auctions_collection.count_documents({})

    pipeline = [
        {
            "$group": {
                "_id": "closed",
                "count": {"$sum": 1}
            }
        }
    ]
    result = await history_collection.aggregate(pipeline).to_list(length=None)

    auctions_closed_count = result[0]["count"] if result else 0

    stats = {
        "auctions_active": auctions_active_count,
        "auctions_closed": auctions_closed_count
    }

    return stats
