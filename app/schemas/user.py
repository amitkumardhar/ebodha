
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.models.user import UserRole
from app.schemas.token import TokenPayload

class UserBase(BaseModel):
    name: str
    gender: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    # role: UserRole  <-- Removed single role
    is_active: Optional[bool] = True

class UserRoleEntry(BaseModel):
    role: UserRole
    class Config:
        orm_mode = True

class UserCreate(UserBase):
    id: str # Student ID or Login ID
    password: str
    roles: List[UserRole]

class UserUpdate(UserBase):
    password: Optional[str] = None
    roles: Optional[List[UserRole]] = None

class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class UserInDBBase(UserBase):
    id: str
    roles: List[UserRoleEntry] = []
    
    class Config:
        orm_mode = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str
