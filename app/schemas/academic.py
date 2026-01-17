
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class CalendarEventBase(BaseModel):
    name: str
    start_date: date
    end_date: date

class CalendarEventCreate(CalendarEventBase):
    semester_id: int

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

class Semester(SemesterBase):
    id: int
    calendar_events: List[CalendarEvent] = []
    class Config:
        orm_mode = True
