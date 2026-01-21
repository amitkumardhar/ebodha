from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.discipline import Discipline
from app.models.user import User
from app.schemas.discipline import Discipline as DisciplineSchema, DisciplineCreate, DisciplineUpdate

router = APIRouter()

@router.get("/", response_model=List[DisciplineSchema])
def read_disciplines(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve disciplines.
    """
    disciplines = db.query(Discipline).offset(skip).limit(limit).all()
    return disciplines

@router.post("/", response_model=DisciplineSchema)
def create_discipline(
    *,
    db: Session = Depends(deps.get_db),
    discipline_in: DisciplineCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new discipline.
    """
    discipline = db.query(Discipline).filter(Discipline.code == discipline_in.code).first()
    if discipline:
        raise HTTPException(status_code=400, detail="Discipline with this code already exists")
    
    discipline = Discipline(**discipline_in.dict())
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return discipline

@router.get("/{code}", response_model=DisciplineSchema)
def read_discipline(
    code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get discipline by code.
    """
    discipline = db.query(Discipline).filter(Discipline.code == code).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    return discipline

@router.put("/{code}", response_model=DisciplineSchema)
def update_discipline(
    *,
    db: Session = Depends(deps.get_db),
    code: str,
    discipline_in: DisciplineUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update discipline.
    """
    discipline = db.query(Discipline).filter(Discipline.code == code).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    update_data = discipline_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(discipline, field, value)
    
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return discipline

@router.delete("/{code}")
def delete_discipline(
    *,
    db: Session = Depends(deps.get_db),
    code: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete (deactivate) discipline.
    """
    discipline = db.query(Discipline).filter(Discipline.code == code).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    discipline.is_active = False
    db.add(discipline)
    db.commit()
    return {"message": "Discipline deactivated successfully"}
