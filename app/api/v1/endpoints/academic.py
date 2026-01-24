
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.academic import Semester, CalendarEvent
from app.models.user import User
from app.schemas.academic import Semester as SemesterSchema, SemesterCreate, SemesterUpdate, CalendarEvent as CalendarEventSchema, CalendarEventCreate

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

from app.schemas.academic import CalendarEventUpdate

@router.put("/events/{event_id}", response_model=CalendarEventSchema)
def update_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    event_in: CalendarEventUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a calendar event.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
        
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}")
def delete_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a calendar event.
    """
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
        
    db.delete(event)
    db.commit()
    return {"message": "Calendar event deleted"}



@router.put("/semesters/{semester_id}", response_model=SemesterSchema)
def update_semester(
    *,
    db: Session = Depends(deps.get_db),
    semester_id: int,
    semester_in: SemesterUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a semester.
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    update_data = semester_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(semester, field, value)
        
    db.add(semester)
    db.commit()
    db.refresh(semester)
    return semester

@router.delete("/semesters/{semester_id}")
def delete_semester(
    *,
    db: Session = Depends(deps.get_db),
    semester_id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a semester.
    """
    semester = db.query(Semester).filter(Semester.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    # Check for dependencies (offerings)
    from app.models.course import CourseOffering
    offerings = db.query(CourseOffering).filter(CourseOffering.semester_id == semester_id).first()
    if offerings:
        raise HTTPException(status_code=400, detail="Cannot delete semester with existing offerings")
        
    db.delete(semester)
    db.commit()
    return {"message": "Semester deleted successfully"}
