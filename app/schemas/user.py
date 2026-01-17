
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole
from app.schemas.token import TokenPayload

class UserBase(BaseModel):
    name: str
    gender: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role: UserRole
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    id: str # Student ID or Login ID
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: str
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
