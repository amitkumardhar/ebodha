
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Checking imports...")
    from app.main import app
    from app.core.config import settings
    from app.db.base import Base
    print("Imports successful.")

    print("Checking SQLAlchemy models...")
    # Create an in-memory SQLite database for testing model creation
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    print("SQLAlchemy models created successfully in memory.")
    
    print("Checking Pydantic schemas...")
    from app.schemas.user import UserCreate
    from app.schemas.academic import SemesterCreate
    from app.schemas.course import CourseCreate
    from app.schemas.examination import ExaminationCreate
    print("Pydantic schemas imported successfully.")

    print("Verification complete.")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
