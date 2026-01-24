
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class CalendarEventBase(BaseModel):
    name: str
    start_date: date
    end_date: date

class CalendarEventCreate(CalendarEventBase):
    semester_id: int

class CalendarEventUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class CalendarEvent(CalendarEventBase):
    id: int
    semester_id: int
    class Config:
        orm_mode = True

class SemesterBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    is_active: Optional[bool] = False

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class Semester(SemesterBase):
    id: int
    calendar_events: List[CalendarEvent] = []
    class Config:
        orm_mode = True
