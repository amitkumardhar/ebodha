
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.mongodb import init_mongodb
from app.api.v1.api import api_router
from app.core.middleware import LoggingMiddleware

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.add_middleware(LoggingMiddleware)
 
# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",  # Allows all http and https origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



@app.on_event("startup")
async def startup_event():
    # Initialize MongoDB
    await init_mongodb()
    
    # Create SQLAlchemy tables if they don't exist
    from app.db.session import engine
    from app.db.base import Base
    Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Welcome to eBodha API"}
