
from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.db.base_class import Base

class CourseCategory(str, enum.Enum):
    CORE = "Core Course"
    ELECTIVE = "Elective"
    THESIS = "MTech Thesis"
    PROJECT = "MTech Project"

class Course(Base):
    code = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(Enum(CourseCategory), nullable=False)
    lecture_credits = Column(Integer, default=0)
    tutorial_credits = Column(Integer, default=0)
    practice_credits = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    offerings = relationship("CourseOffering", back_populates="course")

class CourseOffering(Base):
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, ForeignKey("course.code"), nullable=False)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    
    course = relationship("Course", back_populates="offerings")
    semester = relationship("Semester", back_populates="course_offerings")
    
    teachers = relationship("TeacherCourse", back_populates="course_offering")
    registrations = relationship("Registration", back_populates="course_offering")
    examinations = relationship("Examination", back_populates="course_offering")

class TeacherCourse(Base):
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("user.id"), nullable=False)
    course_offering_id = Column(Integer, ForeignKey("courseoffering.id"), nullable=False)
    
    course_offering = relationship("CourseOffering", back_populates="teachers")
    teacher = relationship("User")
