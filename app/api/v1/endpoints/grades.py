
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.examination import GradeMapping
from app.models.user import User
from app.schemas.examination import GradeMapping as GradeMappingSchema, GradeMappingCreate

router = APIRouter()

@router.get("/mappings", response_model=List[GradeMappingSchema])
def read_grade_mappings(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve grade mappings.
    """
    mappings = db.query(GradeMapping).offset(skip).limit(limit).all()
    return mappings

@router.post("/mappings", response_model=List[GradeMappingSchema])
def update_grade_mappings(
    *,
    db: Session = Depends(deps.get_db),
    mappings_in: List[GradeMappingCreate],
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update or create grade mappings.
    """
    # For simplicity, we can clear existing and re-create, or update/insert.
    # Let's do update/insert based on grade.
    results = []
    for mapping_in in mappings_in:
        mapping = db.query(GradeMapping).filter(GradeMapping.grade == mapping_in.grade).first()
        if mapping:
            mapping.points = mapping_in.points
        else:
            mapping = GradeMapping(grade=mapping_in.grade, points=mapping_in.points)
            db.add(mapping)
        db.commit()
        db.refresh(mapping)
        results.append(mapping)
    return results
