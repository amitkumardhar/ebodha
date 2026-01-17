
from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Semester(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=False)
    
    calendar_events = relationship("CalendarEvent", back_populates="semester")
    course_offerings = relationship("CourseOffering", back_populates="semester")

class CalendarEvent(Base):
    id = Column(Integer, primary_key=True, index=True)
    semester_id = Column(Integer, ForeignKey("semester.id"), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    semester = relationship("Semester", back_populates="calendar_events")
