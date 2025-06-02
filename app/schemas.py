from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# 1) SCHEMATY UŻYTKOWNIKÓW

class UserBase(BaseModel):
    username: str = Field(..., example="JanKowalski")
    email: EmailStr = Field(..., example="jan@example.com")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, example="mojeHaslo123")


class UserOut(UserBase):
    id: str
    role: str


# Tokeny JWT
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    id: Optional[str] = None
    role: Optional[str] = None


class TokenRefreshRequest(BaseModel):
    refresh_token: str


# 2) SCHEMATY AUKCJI

class AuctionCreate(BaseModel):
    title: str = Field(..., example="Laptop Lenovo")
    description: Optional[str] = Field(None, example="Używany, stan bardzo dobry")
    starting_price: float = Field(..., gt=0, example=100.0)


class AuctionOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    current_price: float
    created_at: datetime


class AuctionHistoryOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    owner_id: str
    created_at: datetime
    closed_at: datetime
    winner_id: Optional[str]
    final_price: Optional[float]


# 3) SCHEMATY OFERT (BID)

class BidCreate(BaseModel):
    amount: float = Field(..., gt=0, example=150.0)


class BidOut(BaseModel):
    id: str
    auction_id: str
    user_id: str
    amount: float
    timestamp: datetime
