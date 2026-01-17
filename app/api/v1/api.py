
from fastapi import APIRouter
from app.api.v1.endpoints import login, users, academic, courses, registration, examination, grades

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(academic.router, prefix="/academic", tags=["academic"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(registration.router, prefix="/registrations", tags=["registrations"])
api_router.include_router(examination.router, prefix="/examinations", tags=["examinations"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
