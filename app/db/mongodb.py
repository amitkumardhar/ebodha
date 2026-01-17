
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

from app.models.log import APILog

async def init_mongodb():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    # We will add document models here later
    await init_beanie(database=client[settings.MONGODB_DB_NAME], document_models=[APILog])
