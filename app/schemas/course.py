
from pydantic import BaseModel
from typing import Optional, List
from app.models.course import CourseCategory

class CourseBase(BaseModel):
    name: str
    category: CourseCategory
    lecture_credits: int = 0
    tutorial_credits: int = 0
    practice_credits: int = 0
    is_active: Optional[bool] = True

class CourseCreate(CourseBase):
    code: str

class Course(CourseBase):
    code: str
    class Config:
        orm_mode = True

class CourseOfferingBase(BaseModel):
    course_code: str
    semester_id: int

class CourseOfferingCreate(CourseOfferingBase):
    pass

class CourseOffering(CourseOfferingBase):
    id: int
    class Config:
        orm_mode = True
