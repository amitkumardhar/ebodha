
from sqlalchemy import Column, String, Boolean, Enum
import enum
from app.db.base_class import Base

class UserRole(str, enum.Enum):
    STUDENT = "student"
    ALUMNI = "alumni"
    TEACHER = "teacher"
    ADMIN = "administrator"

class User(Base):
    id = Column(String, primary_key=True, index=True) # Student ID or Login ID
    name = Column(String, nullable=False)
    gender = Column(String)
    address = Column(String)
    phone_number = Column(String)
    email = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
