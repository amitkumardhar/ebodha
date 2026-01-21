from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DisciplineBase(BaseModel):
    name: str
    is_active: Optional[bool] = True

class DisciplineCreate(DisciplineBase):
    code: str

class DisciplineUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None

class Discipline(DisciplineBase):
    code: str
    created_at: datetime
    
    class Config:
        orm_mode = True
