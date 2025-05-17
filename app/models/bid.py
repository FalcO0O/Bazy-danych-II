from pydantic import BaseModel
from datetime import datetime

class Bid(BaseModel):
    user_id: str
    amount: float
    created_at: datetime