
from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.id == user_in.id).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = User(
        id=user_in.id,
        name=user_in.name,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        gender=user_in.gender,
        address=user_in.address,
        phone_number=user_in.phone_number,
        is_active=user_in.is_active,
    )
    db.add(user)
    db.flush()  # Flush to get user in session
    
    # Add roles
    from app.models.user import UserRoleEntry
    for role in user_in.roles:
        role_entry = UserRoleEntry(user_id=user.id, role=role)
        db.add(role_entry)
    
    db.commit()
    db.refresh(user)
    return user

@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}/role", response_model=UserSchema)
def update_user_role(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    role: UserRole = Body(..., embed=True),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Add a role to user (if not already present).
    """
    from app.models.user import UserRoleEntry
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already has this role
    existing_role = db.query(UserRoleEntry).filter(
        UserRoleEntry.user_id == user_id,
        UserRoleEntry.role == role
    ).first()
    
    if not existing_role:
        role_entry = UserRoleEntry(user_id=user_id, role=role)
        db.add(role_entry)
        db.commit()
    
    db.refresh(user)
    return user

from app.schemas.user import UserPasswordUpdate

@router.put("/me/password", response_model=Any)
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    password_in: UserPasswordUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Change current user password.
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if not security.verify_password(password_in.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
        
    user.hashed_password = security.get_password_hash(password_in.new_password)
    db.add(user)
    db.commit()
    
    return {"message": "Password updated successfully"}
