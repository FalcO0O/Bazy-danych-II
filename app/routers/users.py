from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas import UserOut, BidOut
from dependencies import get_current_active_user, get_current_admin
from database import users_collection, bids_collection
from bson import ObjectId

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", response_model=List[UserOut])
async def list_users(admin_user: dict = Depends(get_current_admin)):
    """
    Lista wszystkich użytkowników - dostępne tylko dla administratora.
    """
    users_cursor = users_collection.find()
    users = []
    async for u in users_cursor:
        users.append(UserOut(
            id=str(u["_id"]),
            username=u["username"],
            email=u["email"],
            role=u.get("role", "user")
        ))
    return users


@router.get("/{user_id}", response_model=UserOut)
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_active_user)):
    """
    Pobranie profilu konkretnego użytkownika.
    Admin może pobrać każdego użytkownika, zwykły user tylko siebie.
    """
    if current_user.get("role") != "admin" and str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień")
    try:
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(status_code=400, detail="Nieprawidłowy identyfikator użytkownika")

    if not user:
        raise HTTPException(status_code=404, detail="Użytkownik nie znaleziony")

    return UserOut(
        id=str(user["_id"]),
        username=user["username"],
        email=user["email"],
        role=user.get("role", "user")
    )


@router.get("/{user_id}/bids", response_model=List[BidOut])
async def get_user_bids(user_id: str, current_user: dict = Depends(get_current_active_user)):
    """
    Historia licytacji (ofert) dla danego użytkownika.
    Tylko właściciel konta lub administrator.
    """
    if current_user.get("role") != "admin" and str(current_user["_id"]) != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień")
    bids_cursor = bids_collection.find({"user_id": user_id})
    bids = []
    async for b in bids_cursor:
        bids.append(BidOut(
            id=str(b["_id"]),
            auction_id=b["auction_id"],
            user_id=b["user_id"],
            amount=b["amount"],
            timestamp=b["timestamp"]
        ))
    return bids
