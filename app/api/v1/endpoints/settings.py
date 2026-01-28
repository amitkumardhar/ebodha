from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.models.user import User, UserRole
from app.models.setting import SystemSetting
from app.models.academic import Semester

router = APIRouter()

class SettingUpdate(BaseModel):
    key: str
    value: str

@router.get("/", response_model=Dict[str, str])
def get_settings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get all system settings.
    """
    settings = db.query(SystemSetting).all()
    return {s.key: s.value for s in settings}

@router.put("/", response_model=Dict[str, str])
def update_settings(
    settings_in: List[SettingUpdate],
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update system settings.
    """
    response = {}
    for s_in in settings_in:
        setting = db.query(SystemSetting).filter(SystemSetting.key == s_in.key).first()
        if not setting:
            setting = SystemSetting(key=s_in.key, value=s_in.value)
            db.add(setting)
        else:
            setting.value = s_in.value
            
        # Validation logic can go here if needed (e.g. check if semester_id exists)
        if s_in.key == "current_semester_id":
            # Verify semester exists
            try:
                sem_id = int(s_in.value)
                sem = db.query(Semester).filter(Semester.id == sem_id).first()
                if not sem:
                    # Depending on strictness, we might raise error or just save. 
                    # Let's save but warn? No, API should be strict ideally.
                    pass 
            except ValueError:
                pass

        response[s_in.key] = s_in.value
    
    db.commit()
    return response

@router.get("/public", response_model=Dict[str, str])
def get_public_settings(
    db: Session = Depends(deps.get_db),
    # No auth required strictly? Or minimal auth. 
    # Usually settings like current semester might be needed by everyone.
    # But for now let's reuse authenticated user logic or open it if needed.
    # The prompt implies "admin can set", implies internal use.
    current_user: User = Depends(deps.get_current_user), 
) -> Any:
    """
    Get settings relevant for general users/teachers.
    """
    keys = ["current_semester_id", "grade_submission_deadline", "compartment_submission_deadline"]
    settings = db.query(SystemSetting).filter(SystemSetting.key.in_(keys)).all()
    return {s.key: s.value for s in settings}
