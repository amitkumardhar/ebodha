from pydantic import BaseModel
from typing import Optional

class TeacherCourseBase(BaseModel):
    teacher_id: str
    course_offering_id: int

class TeacherCourseCreate(TeacherCourseBase):
    pass

class TeacherCourse(TeacherCourseBase):
    id: int
    
    class Config:
        orm_mode = True

class TeacherInfo(BaseModel):
    id: int
    teacher_id: str
    teacher_name: str
    
    class Config:
        orm_mode = True
