from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.setting import SystemSetting
from app.models.user import User, UserRole

def check_grade_submission_deadline(db: Session, user: User) -> None:
    """
    Check if the current date is before the grade submission deadline.
    Only checks for TEACHER role (Admin overrides).
    Raises ValueError if deadline has passed.
    """
    if user.current_role == UserRole.ADMIN:
        return

    setting = db.query(SystemSetting).filter(SystemSetting.key == "grade_submission_deadline").first()
    if not setting or not setting.value:
        return # No deadline set

    try:
        deadline = datetime.strptime(setting.value, "%Y-%m-%d").date()
        if date.today() > deadline:
            raise ValueError("Last date of grade submission has passed")
    except ValueError as e:
        if "Last date" in str(e):
             raise e
        # Ignore parse errors? Or block? Safe to ignore if format is bad, but admin should ensure format.
        pass

def check_compartment_submission_deadline(db: Session, user: User) -> None:
    """
    Check if the current date is before the compartment submission deadline.
    Only checks for TEACHER role.
    Raises ValueError if deadline has passed.
    """
    if user.current_role == UserRole.ADMIN:
        return

    setting = db.query(SystemSetting).filter(SystemSetting.key == "compartment_submission_deadline").first()
    if not setting or not setting.value:
        return

    try:
        deadline = datetime.strptime(setting.value, "%Y-%m-%d").date()
        if date.today() > deadline:
            raise ValueError("Last date of compartment grade submission has passed")
    except ValueError as e:
        if "Last date" in str(e):
             raise e
        pass
