from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .bid import Bid

class AuctionHistory(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str]
    media: List[str]
    start_date: datetime
    end_date: datetime
    status: str
    winner_user_id: Optional[str]
    bids: List[Bid]
