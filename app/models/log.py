
from typing import Optional
from datetime import datetime
from beanie import Document
from pydantic import Field

class APILog(Document):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    endpoint: str
    method: str
    user_id: Optional[str] = None
    role: Optional[str] = None
    remark: Optional[str] = None
    status_code: int

    class Settings:
        name = "api_logs"
