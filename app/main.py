
from fastapi import FastAPI
from app.core.config import settings
from app.db.mongodb import init_mongodb
from app.api.v1.api import api_router
from app.core.middleware import LoggingMiddleware

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.add_middleware(LoggingMiddleware)

@app.on_event("startup")
async def startup_event():
    await init_mongodb()

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to eBodha API"}
