import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.main import app
from app.db.base_class import Base
from app.api import deps
from app.models.user import User, UserRole, UserRoleEntry
from app.models.discipline import Discipline
from app.core import security

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_bulk_users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

client = TestClient(app)

def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create an admin user for authentication
    admin_user = User(
        id="admin",
        name="Admin User",
        email="admin@example.com",
        hashed_password=security.get_password_hash("adminpass"),
        is_active=True
    )
    db.add(admin_user)
    admin_role = UserRoleEntry(user_id="admin", role=UserRole.ADMIN)
    db.add(admin_role)
    
    # Create a discipline
    discipline = Discipline(code="CSE", name="Computer Science")
    db.add(discipline)
    
    db.commit()
    db.close()

def test_bulk_upload_users():
    setup_db()
    
    # Mock authentication
    with patch("app.api.deps.get_current_user") as mock_get_current_user:
        admin_user = MagicMock()
        admin_user.id = "admin"
        admin_user.current_role = UserRole.ADMIN
        mock_get_current_user.return_value = admin_user
        
        # Prepare CSV content
        csv_content = (
            "id,name,email,password,gender,address,phone_number,discipline_code,roles\n"
            "student1,Student One,s1@example.com,pass1,Male,Addr1,123,CSE,student\n"
            "teacher1,Teacher One,t1@example.com,pass2,Female,Addr2,456,,teacher\n"
            "both1,Both Roles,b1@example.com,pass3,Other,Addr3,789,CSE,student;teacher\n"
            "invalid_disc,Invalid Disc,id@example.com,pass4,Male,Addr4,000,INVALID,student\n"
        )
        
        files = {"file": ("users.csv", csv_content, "text/csv")}
        response = client.post("/api/v1/users/bulk-upload", files=files)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["users_created"] == 3
        assert len(data["errors"]) == 1
        assert "Discipline INVALID not found" in data["errors"][0]
        
        # Verify users in DB
        db = TestingSessionLocal()
        s1 = db.query(User).filter(User.id == "student1").first()
        assert s1 is not None
        assert s1.discipline_code == "CSE"
        assert len(s1.roles) == 1
        assert s1.roles[0].role == UserRole.STUDENT
        
        t1 = db.query(User).filter(User.id == "teacher1").first()
        assert t1 is not None
        assert t1.discipline_code is None
        assert len(t1.roles) == 1
        assert t1.roles[0].role == UserRole.TEACHER
        
        b1 = db.query(User).filter(User.id == "both1").first()
        assert b1 is not None
        assert len(b1.roles) == 2
        roles = [r.role for r in b1.roles]
        assert UserRole.STUDENT in roles
        assert UserRole.TEACHER in roles
        
        db.close()
        print("Verification successful!")

if __name__ == "__main__":
    try:
        test_bulk_upload_users()
    finally:
        if os.path.exists("test_bulk_users.db"):
            os.remove("test_bulk_users.db")
