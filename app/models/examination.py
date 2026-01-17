
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class GradeMapping(Base):
    id = Column(Integer, primary_key=True, index=True)
    grade = Column(String, unique=True, nullable=False)
    points = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Registration(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("user.id"), nullable=False)
    course_offering_id = Column(Integer, ForeignKey("courseoffering.id"), nullable=False)
    grade = Column(String, nullable=True)
    grade_point = Column(Float, nullable=True)
    
    student = relationship("User")
    course_offering = relationship("CourseOffering", back_populates="registrations")
    marks = relationship("Marks", back_populates="registration")

class Examination(Base):
    id = Column(Integer, primary_key=True, index=True)
    course_offering_id = Column(Integer, ForeignKey("courseoffering.id"), nullable=False)
    name = Column(String, nullable=False)
    max_marks = Column(Float, nullable=False)
    date = Column(Date, nullable=True)
    
    course_offering = relationship("CourseOffering", back_populates="examinations")
    marks = relationship("Marks", back_populates="examination")

class Marks(Base):
    id = Column(Integer, primary_key=True, index=True)
    registration_id = Column(Integer, ForeignKey("registration.id"), nullable=False)
    examination_id = Column(Integer, ForeignKey("examination.id"), nullable=False)
    marks_obtained = Column(Float, nullable=False)
    
    registration = relationship("Registration", back_populates="marks")
    examination = relationship("Examination", back_populates="marks")
