from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List
from datetime import datetime
from bson import ObjectId
from pymongo.errors import OperationFailure
from bson.errors import InvalidId
from asyncio import sleep

from schemas import AuctionCreate, AuctionOut, BidCreate, BidOut
from database import auctions_collection, bids_collection, history_collection, get_client
from dependencies import get_current_active_user, get_current_admin
from utils import log_action

router = APIRouter(
    prefix="/auctions",
    tags=["auctions"]
)


@router.post("", response_model=AuctionOut)
async def create_auction(auction: AuctionCreate, current_user: dict = Depends(get_current_active_user)):
    """
    Tworzenie nowej aukcji - tylko zalogowani użytkownicy.
    - Ustawiamy owner_id na _id użytkownika w kolekcji.
    - current_price przyjmujemy jako starting_price.
    """
    auction_data = auction.model_dump()
    auction_data["owner_id"] = str(current_user["_id"])
    auction_data["current_price"] = auction.starting_price
    auction_data["created_at"] = datetime.now()

    result = await auctions_collection.insert_one(auction_data)
    new_auc = await auctions_collection.find_one({"_id": result.inserted_id})

    await log_action(str(current_user["_id"]), "create_auction", f"Aukcja utworzona: {new_auc['title']}")

    return AuctionOut(
        id=str(new_auc["_id"]),
        title=new_auc["title"],
        description=new_auc.get("description"),
        owner_id=new_auc["owner_id"],
        current_price=new_auc["current_price"],
        created_at=new_auc["created_at"]
    )


@router.get("", response_model=List[AuctionOut])
async def list_active_auctions():
    """
    Lista wszystkich aktywnych aukcji.
    """
    cursor = auctions_collection.find()
    auctions = []
    async for auc in cursor:
        auctions.append(AuctionOut(
            id=str(auc["_id"]),
            title=auc["title"],
            description=auc.get("description"),
            owner_id=auc["owner_id"],
            current_price=auc["current_price"],
            created_at=auc["created_at"]
        ))
    return auctions


@router.get("/{auction_id}", response_model=AuctionOut)
async def get_auction(auction_id: str):
    """
    Szuka aukcji po podanym ID. Jeśli nie ma → 404.
    """
    try:
        auc = await auctions_collection.find_one({"_id": ObjectId(auction_id)})
    except:
        raise HTTPException(status_code=400, detail="Nieprawidłowy identyfikator aukcji")
    if not auc:
        raise HTTPException(status_code=404, detail="Aukcja nie znaleziona")
    return AuctionOut(
        id=str(auc["_id"]),
        title=auc["title"],
        description=auc.get("description"),
        owner_id=auc["owner_id"],
        current_price=auc["current_price"],
        created_at=auc["created_at"]
    )

@router.post("/{auction_id}/bid", response_model=BidOut)
async def place_bid(
    auction_id: str,
    bid: BidCreate,
    current_user: dict = Depends(get_current_active_user)
):
    for attempt in range(5):
        try:
            async with await get_client().start_session() as session:
                async with session.start_transaction():
                    try:
                        auc = await auctions_collection.find_one(
                            {"_id": ObjectId(auction_id)}, 
                            session=session
                        )
                    except InvalidId:
                        raise HTTPException(status_code=400, detail="Nieprawidłowy identyfikator aukcji")

                    if not auc:
                        raise HTTPException(status_code=404, detail="Aukcja nie znaleziona")

                    if bid.amount <= auc["current_price"]:
                        raise HTTPException(status_code=400, detail="Kwota oferty musi być wyższa niż bieżąca cena")

                    await auctions_collection.update_one(
                        {"_id": ObjectId(auction_id)},
                        {"$set": {"current_price": bid.amount}},
                        session=session
                    )

                    bid_data = {
                        "auction_id": auction_id,
                        "user_id": str(current_user["_id"]),
                        "amount": bid.amount,
                        "timestamp": datetime.utcnow()
                    }
                    result = await bids_collection.insert_one(bid_data, session=session)
                    new_bid = await bids_collection.find_one({"_id": result.inserted_id}, session=session)

                    await log_action(str(current_user["_id"]), "bid", f"Oferta {bid.amount} na aukcji {auction_id}")

                    return BidOut(
                        id=str(new_bid["_id"]),
                        auction_id=new_bid["auction_id"],
                        user_id=new_bid["user_id"],
                        amount=new_bid["amount"],
                        timestamp=new_bid["timestamp"]
                    )
        except HTTPException:
            raise
        except OperationFailure as e:
            if "TransientTransactionError" in str(e) or e.has_error_label("TransientTransactionError"):
                if attempt == 4:
                    raise HTTPException(status_code=500, detail="Przekroczono maksymalną liczbę prób transakcji")
                await sleep(0.1)
                continue
            else:
                raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")


@router.post("/{auction_id}/close")
async def close_auction(
    auction_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Zamykanie aukcji (przenosimy ją do historii).
    Tylko:
    - właściciel aukcji (owner_id) lub
    - administrator.
    """

    async with await get_client().start_session() as session:
        async with session.start_transaction():
            # Sprawdzenie czy aukcja istnieje
            try:
                auc = await auctions_collection.find_one({"_id": ObjectId(auction_id)}, session = session)
            except:
                raise HTTPException(status_code=400, detail="Nieprawidłowy identyfikator aukcji")
            if not auc:
                raise HTTPException(status_code=404, detail="Aukcja nie znaleziona")

            # Sprawdzenie uprawnień
            if auc["owner_id"] != str(current_user["_id"]) and current_user.get("role") != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Brak uprawnień do zakończenia tej aukcji")

            # Pobranie wszystkich ofert z bids_collection
            bids_cursor = bids_collection.find({"auction_id": auction_id}, session = session)
            bids_list = []
            async for b in bids_cursor:
                bids_list.append(b)

            # Ustalenie zwycięzcy:
            if bids_list:
                highest = max(bids_list, key=lambda x: x["amount"])
                winner_id = highest["user_id"]
                final_price = highest["amount"]
            else:
                winner_id = None
                final_price = auc["current_price"]

            # Przygotowanie dokumentu do kolekcji history
            history_doc = {
                "title": auc["title"],
                "description": auc.get("description"),
                "owner_id": auc["owner_id"],
                "created_at": auc["created_at"],
                "closed_at": datetime.now(),
                "winner_id": winner_id,
                "final_price": final_price
            }
            await history_collection.insert_one(history_doc, session = session)

            # Usunięcie aukcji z aktywnych + usunięcie jej oferty z bids_collection
            await auctions_collection.delete_one({"_id": ObjectId(auction_id)}, session = session)
            await bids_collection.delete_many({"auction_id": auction_id}, session = session)

            await log_action(str(current_user["_id"]), "close_auction", f"Zakończono aukcję {auction_id}")

            return {
                "message": "Aukcja została zakończona",
                "winner_id": winner_id,
                "final_price": final_price
            }

@router.patch("/{auction_id}", response_model=AuctionOut)
async def admin_edit_auction(
    auction_id: str,
    updates: dict = Body(...),
    current_admin: dict = Depends(get_current_admin)
):
    """
    Administrator edytuje dane aukcji. 
    Dozwolone pola: title, description, starting_price.
    Jeśli istnieją oferty, nie można zmienić starting_price.
    """
    allowed_fields = {"title", "description", "starting_price"}

    # Walidacja pól
    if not updates:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    
    for key in updates:
        if key not in allowed_fields:
            raise HTTPException(status_code=400, detail=f"Pole '{key}' nie może być edytowane")

    # Pobranie aukcji
    try:
        auc = await auctions_collection.find_one({"_id": ObjectId(auction_id)})
    except:
        raise HTTPException(status_code=400, detail="Nieprawidłowy identyfikator aukcji")

    if not auc:
        raise HTTPException(status_code=404, detail="Aukcja nie znaleziona")

    # Jeśli są oferty zablokuj zmianę starting_price
    has_bids = await bids_collection.find_one({"auction_id": auction_id})
    if "starting_price" in updates and has_bids:
        raise HTTPException(status_code=400, detail="Nie można zmienić ceny startowej - są już oferty")

    # Aktualizacja
    await auctions_collection.update_one(
        {"_id": ObjectId(auction_id)},
        {"$set": updates}
    )

    updated = await auctions_collection.find_one({"_id": ObjectId(auction_id)})

    await log_action(str(current_admin["_id"]), "edit_auction", f"Edytowano aukcję {auction_id}")

    return AuctionOut(
        id=str(updated["_id"]),
        title=updated["title"],
        description=updated.get("description"),
        owner_id=updated["owner_id"],
        current_price=updated["current_price"],
        created_at=updated["created_at"]
    )
