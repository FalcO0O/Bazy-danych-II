from fastapi import APIRouter, HTTPException
from pymongo.errors import PyMongoError
from models.user import UserCreate
from database import users_collection
from utils.security import hash_password
from bson import ObjectId
from utils.logger import log_operation, log_info, log_error

router = APIRouter()

@router.post("/register")
async def register_user(user: UserCreate):
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="E-mail already has a registered account!")
    
    hashed = hash_password(user.password)

    try:
        result = await users_collection.insert_one({
            "name": user.name,
            "email":user.email,
            "password_hash":hashed,
            "refresh_tokens":[]
        })
    except PyMongoError as e:
        log_error(f"Error inserting user {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Error inserting user to database")

    log_info(f"User registered: {user.email}")
    await log_operation(
        operation_type="INSERT",
        collection_name="users",
        meta={"user_email": user.email, "user_id":str(result.inserted_id)}
    )

    return {
        "id": str(result.inserted_id),
        "message": "User registered successfully"
    }

__all__ = ["router"]
