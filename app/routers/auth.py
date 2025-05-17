from fastapi import APIRouter, HTTPException
from models.user import UserLogin, Token
from database import users_collection
from utils.security import verify_password, create_access_token
from utils.logger import log_operation, log_info, log_error


router = APIRouter()

@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await users_collection.find_one({"email": user.email})
    if not db_user:
        log_error(f"Login failed: Email {user.email} not found")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    if not verify_password(user.password, db_user["password_hash"]):
        log_error(f"Login failed: Wrong password for {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email})

    log_info(f"User logged in: {user.email}")
    await log_operation(
        operation_type="LOGIN",
        collection_name="users",
        meta={"user_email": user.email, "user_id": str(db_user["_id"])}
    )

    return {"access_token": access_token, "token_type": "bearer"}

__all__ = ["router"]