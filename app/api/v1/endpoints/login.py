
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token, TokenPayload

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), 
    form_data: OAuth2PasswordRequestForm = Depends(),
    role: str = None
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.id == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Determine role
    user_roles = [r.role for r in user.roles]
    if not user_roles:
         raise HTTPException(status_code=400, detail="User has no assigned roles")
         
    selected_role = None
    if role:
        if role not in user_roles:
            raise HTTPException(status_code=400, detail="User does not have this role")
        selected_role = role
    else:
        # Default to first role
        selected_role = user_roles[0]

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, role=selected_role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/switch-role", response_model=Token)
def switch_role(
    new_role: str,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Switch to a different role without re-login.
    """
    # Verify user has the new role
    # Note: current_user.roles is a list of UserRoleEntry objects
    user_roles = [r.role.value for r in current_user.roles]
    
    if new_role not in user_roles:
        raise HTTPException(status_code=400, detail="User does not have this role")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            current_user.id, role=new_role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

from app.models.token import RevokedToken
from fastapi import status

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    token: str = Depends(deps.reusable_oauth2),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Logout the current user by revoking the token.
    """
    # Calculate expiration time from token
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        expires_at = datetime.fromtimestamp(payload.get("exp"))
        
        revoked_token = RevokedToken(token=token, expires_at=expires_at)
        await revoked_token.create()
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Logout failed: {str(e)}")
