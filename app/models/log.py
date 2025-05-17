from pydantic import BaseModel
from datetime import datetime
from typing import Any

class LogEntry(BaseModel):
    operation_type: str
    timestamp: datetime
    meta: dict
    collection: str
