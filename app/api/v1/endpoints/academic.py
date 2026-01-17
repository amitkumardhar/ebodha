
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.academic import Semester, CalendarEvent
from app.models.user import User
from app.schemas.academic import Semester as SemesterSchema, SemesterCreate, CalendarEvent as CalendarEventSchema, CalendarEventCreate

router = APIRouter()

@router.get("/semesters/", response_model=List[SemesterSchema])
def read_semesters(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve semesters.
    """
    semesters = db.query(Semester).offset(skip).limit(limit).all()
    return semesters

@router.post("/semesters/", response_model=SemesterSchema)
def create_semester(
    *,
    db: Session = Depends(deps.get_db),
    semester_in: SemesterCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new semester.
    """
    semester = Semester(**semester_in.dict())
    db.add(semester)
    db.commit()
    db.refresh(semester)
    return semester

@router.post("/events/", response_model=CalendarEventSchema)
def create_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: CalendarEventCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new calendar event.
    """
    event = CalendarEvent(**event_in.dict())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
