from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .bid import Bid

class AuctionCreate(BaseModel):
    name: str
    category: str
    description: Optional[str]
    media: List[str]
    start_date: datetime
    end_date: datetime
    status: str
    user_id: str
    starting_price: float

class AuctionDB(AuctionCreate):
    id: str
    bids: List[Bid] = []
