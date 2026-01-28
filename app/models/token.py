
from datetime import datetime
from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING

class RevokedToken(Document):
    token: str
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    class Settings:
        name = "revoked_tokens"
        indexes = [
            IndexModel([("expires_at", ASCENDING)], expireAfterSeconds=0)
        ]

class UserGlobalRevocation(Document):
    user_id: str
    revoked_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "user_global_revocations"
        indexes = [
            IndexModel([("user_id", ASCENDING)], unique=True)
        ]
