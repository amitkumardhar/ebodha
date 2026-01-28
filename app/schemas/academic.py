
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

class AcademicHistoryCourse(BaseModel):
    code: str
    name: str
    credits: float  # Total credits (L+T+0.5*P)
    original_grade: Optional[str]
    compartment_grade: Optional[str]
    course_grade: Optional[str] # Final effective grade
    grade_point: Optional[float]

class AcademicHistorySemester(BaseModel):
    semester_id: int
    semester_name: str
    start_date: date
    sgpa: Optional[float]
    courses: List[AcademicHistoryCourse]

class AcademicHistory(BaseModel):
    student_id: str
    student_name: str
    discipline_code: Optional[str]
    discipline_name: Optional[str]
    cgpa: Optional[float]
    semesters: List[AcademicHistorySemester]
