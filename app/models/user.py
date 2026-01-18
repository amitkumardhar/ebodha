
from sqlalchemy import Column, String, Boolean, Enum, Integer, ForeignKey
from sqlalchemy.orm import relationship
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
    is_active = Column(Boolean, default=True)
    
    roles = relationship("UserRoleEntry", back_populates="user", cascade="all, delete-orphan")

class UserRoleEntry(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    
    user = relationship("User", back_populates="roles")
