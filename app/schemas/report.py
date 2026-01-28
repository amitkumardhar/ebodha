
from typing import List, Optional
from pydantic import BaseModel

class ExamMarksReport(BaseModel):
    examination_id: int
    exam_name: str
    max_marks: float
    marks_obtained: float

class CourseInfo(BaseModel):
    code: str
    name: str
    semester_id: int
    credits: str # Formatted L-T-P
    lecture_credits: int
    tutorial_credits: int
    practice_credits: int

class StudentGradeReportItem(BaseModel):
    course: CourseInfo
    grade: Optional[str]
    grade_point: Optional[float]
    compartment_grade: Optional[str] = None
    compartment_grade_point: Optional[float] = None
    marks: List[ExamMarksReport]

class GradeCardRequest(BaseModel):
    student_ids: List[str]
    semester_id: int

class TranscriptRequest(BaseModel):
    student_ids: List[str]
