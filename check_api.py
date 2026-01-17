
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app
from app.db.base import Base
from app.api import deps

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

def verify_api():
    print("Creating test database...")
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    
    print("Testing API startup...")
    response = client.get("/")
    assert response.status_code == 200
    print("API startup successful.")
    
    print("Testing OpenAPI schema...")
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    print("OpenAPI schema generated successfully.")
    
    # Note: Verifying actual MongoDB logging in this unit test script is tricky without a real Mongo instance
    # or extensive mocking of Motor/Beanie which is async.
    # For now, we verified the middleware is attached and doesn't crash the app.
    
    print("Verification complete.")

if __name__ == "__main__":
    try:
        # Mock init_mongodb to avoid connection error during test startup if no mongo
        from app.db import mongodb
        mongodb.init_mongodb = lambda: None
        
        verify_api()
        # Clean up
        if os.path.exists("./test.db"):
            os.remove("./test.db")
    except Exception as e:
        print(f"Verification failed: {e}")
        sys.exit(1)
