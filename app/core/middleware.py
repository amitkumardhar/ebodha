
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt
from app.core.config import settings
from app.models.log import APILog
from app.schemas.token import TokenPayload
from app.core import security
from app.models.user import User
from app.db.session import SessionLocal
import json

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Skip logging for OPTIONS and static files if any (or specific paths)
        if request.method == "OPTIONS":
            return response

        # Extract User Info
        user_id = None
        role = None
        
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
                )
                token_data = TokenPayload(**payload)
                user_id = token_data.sub
                
                # To get role, we might need to query DB or if we embedded it in token.
                # Since we didn't embed role in token, we query DB.
                # Ideally, we should embed role in token to avoid DB hit on every log,
                # but for now let's query.
                # Optimization: Use a cache or embed role in token in next iteration.
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        role = user.role.value
                finally:
                    db.close()
                    
            except Exception:
                pass # Invalid token or other error, treat as anonymous

        # Extract Remark (Query params + Body snippet?)
        # Body is consumed, so we can't easily read it in middleware without tricks.
        # For now, let's log query params and path.
        remark = f"Path: {request.url.path}, Query: {request.query_params}"
        
        # Log to MongoDB
        # Since middleware is async, we can await Beanie
        try:
            log_entry = APILog(
                endpoint=request.url.path,
                method=request.method,
                user_id=user_id,
                role=role,
                remark=remark,
                status_code=response.status_code
            )
            await log_entry.create()
        except Exception as e:
            print(f"Failed to log request: {e}")

        return response
