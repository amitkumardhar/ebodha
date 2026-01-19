import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

# Add project root to path
sys.path.append(os.getcwd())

from app.main import app
from app.db.base import Base
from app.api import deps
from app.models.user import User, UserRole, UserRoleEntry
from app.models.course import Course, CourseCategory, CourseOffering, TeacherCourse
from app.models.academic import Semester
from app.core import security

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_semester_courses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db

def setup_data():
    db = TestingSessionLocal()
    
    # Create Semester
    semester = Semester(
        name="Monsoon 2024",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 12, 1),
        is_active=True
    )
    db.add(semester)
    db.commit()
    db.refresh(semester)
    
    # Create Courses
    c1 = Course(code="CS101", name="Intro to CS", category=CourseCategory.CORE)
    c2 = Course(code="CS102", name="Data Structures", category=CourseCategory.CORE)
    db.add(c1)
    db.add(c2)
    db.commit()
    
    # Create Offerings
    o1 = CourseOffering(course_code="CS101", semester_id=semester.id)
    o2 = CourseOffering(course_code="CS102", semester_id=semester.id)
    db.add(o1)
    db.add(o2)
    db.commit()
    db.refresh(o1)
    db.refresh(o2)
    
    # Create Users
    admin = User(id="admin", name="Admin User", hashed_password="x", email="admin@test.com")
    teacher1 = User(id="t1", name="Teacher One", hashed_password="x", email="t1@test.com")
    teacher2 = User(id="t2", name="Teacher Two", hashed_password="x", email="t2@test.com")
    student = User(id="s1", name="Student One", hashed_password="x", email="s1@test.com")
    
    db.add(admin)
    db.add(teacher1)
    db.add(teacher2)
    db.add(student)
    db.commit()
    
    # Assign Roles
    db.add(UserRoleEntry(user_id="admin", role=UserRole.ADMIN))
    db.add(UserRoleEntry(user_id="t1", role=UserRole.TEACHER))
    db.add(UserRoleEntry(user_id="t2", role=UserRole.TEACHER))
    db.add(UserRoleEntry(user_id="s1", role=UserRole.STUDENT))
    db.commit()
    
    # Assign Teacher1 to Course 1
    tc = TeacherCourse(teacher_id="t1", course_offering_id=o1.id)
    db.add(tc)
    db.commit()
    
    semester_id = semester.id
    db.close()
    return semester_id

def verify():
    print("Setting up test database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    semester_id = setup_data()
    client = TestClient(app)
    
    print("Verifying Admin Access...")
    token = security.create_access_token("admin", role="administrator")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/courses/semester-courses?semester_id={semester_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    print("Admin sees all courses: PASS")
    
    print("Verifying Teacher 1 Access (Assigned to CS101)...")
    token = security.create_access_token("t1", role="teacher")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/courses/semester-courses?semester_id={semester_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["course_code"] == "CS101"
    print("Teacher 1 sees assigned course: PASS")
    
    print("Verifying Teacher 2 Access (No assignments)...")
    token = security.create_access_token("t2", role="teacher")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/courses/semester-courses?semester_id={semester_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0
    print("Teacher 2 sees no courses: PASS")
    
    print("Verifying Student Access...")
    token = security.create_access_token("s1", role="student")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/courses/semester-courses?semester_id={semester_id}", headers=headers)
    assert response.status_code == 403
    print("Student is forbidden: PASS")
    
    print("All verifications passed!")

if __name__ == "__main__":
    try:
        # Mock init_mongodb
        from app.db import mongodb
        mongodb.init_mongodb = lambda: None
        
        # Mock RevokedToken.find_one
        from unittest.mock import AsyncMock
        from app.models.token import RevokedToken
        RevokedToken.find_one = AsyncMock(return_value=None)
        
        verify()
    except Exception as e:
        import traceback
        with open("traceback.log", "w") as f:
            traceback.print_exc(file=f)
        print(f"Verification failed: {e}")
        sys.exit(1)
    finally:
        if os.path.exists("./test_semester_courses.db"):
            os.remove("./test_semester_courses.db")
