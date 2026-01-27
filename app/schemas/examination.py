
from pydantic import BaseModel
from typing import Optional
from datetime import date

class GradeMappingBase(BaseModel):
    grade: str
    points: float

class GradeMappingCreate(GradeMappingBase):
    pass

class GradeMapping(GradeMappingBase):
    id: int
    class Config:
        orm_mode = True

class ExaminationBase(BaseModel):
    name: str
    max_marks: float
    date: Optional[date] = None

class ExaminationCreate(ExaminationBase):
    course_offering_id: int

class ExaminationUpdate(BaseModel):
    name: Optional[str] = None
    max_marks: Optional[float] = None
    date: Optional[date] = None

class Examination(ExaminationBase):
    id: int
    course_offering_id: int
    class Config:
        orm_mode = True

class RegistrationBase(BaseModel):
    student_id: str
    course_offering_id: int

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationUpdate(BaseModel):
    grade: Optional[str] = None
    # grade_point is now calculated, so we don't allow updating it directly via this schema usually,
    # but for manual overrides we might. For now, let's keep it optional or remove it if strictly auto.
    # The requirement says "automatically calculated", so we remove it from input.

class Registration(RegistrationBase):
    id: int
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    class Config:
        orm_mode = True

class CompartmentRegistrationBase(BaseModel):
    student_id: str
    course_offering_id: int

class CompartmentRegistrationCreate(CompartmentRegistrationBase):
    pass

class CompartmentRegistration(CompartmentRegistrationBase):
    id: int
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    class Config:
        orm_mode = True

class CompartmentGradeUpdate(BaseModel):
    grade: str

class MarkUpdate(BaseModel):
    course_code: str
    semester_id: int
    student_id: str
    exam_name: str
    marks: float

class CompartmentStudentDetails(BaseModel):
    id: int
    student_id: str
    student_name: str
    grade: Optional[str] = None
    grade_point: Optional[float] = None
    original_grade: Optional[str] = None

