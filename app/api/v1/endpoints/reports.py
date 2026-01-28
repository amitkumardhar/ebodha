from typing import Any, List, Optional
from datetime import datetime, date
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api import deps
from app.models.user import User, UserRole
from app.models.discipline import Discipline
from app.schemas.user import User as UserSchema
from app.utils.pdf_generator import pdf_generator
from app.api.v1.endpoints.users import get_user_academic_history

from app.schemas.report import GradeCardRequest, TranscriptRequest

router = APIRouter()

# In-memory task store (Use Celery/Redis in production)
# Format: {task_id: {"status": "processing"|"completed"|"failed", "progress": 0-100, "result": None|bytes, "error": None}}
tasks = {}

def process_grade_cards(task_id: str, student_ids: List[str], semester_id: int, db: Session):
    try:
        tasks[task_id]["status"] = "processing"
        total = len(student_ids)
        files = {}
        
        # Get semester info
        from app.models.academic import Semester
        semester = db.query(Semester).filter(Semester.id == semester_id).first()
        if not semester:
             tasks[task_id]["status"] = "failed"
             tasks[task_id]["error"] = "Semester not found"
             return

        semester_data = {"name": semester.name, "id": semester.id}

        for i, student_id in enumerate(student_ids):
            try:
                from app.services.academic import get_student_academic_history
                # Fetch Academic History using Service
                academic_history = get_student_academic_history(db, student_id)
                if not academic_history: continue
                
                # Filter/Find Target Semester Courses from History
                # We need to reconstruct the data structure for PDF generator
                # The service returns AcademicHistory object
                
                student_info = {
                    "id": academic_history.student_id,
                    "name": academic_history.student_name,
                    "discipline_name": academic_history.discipline_name or "N/A",
                    "sgpa": "N/A",
                    "cgpa": f"{academic_history.cgpa:.2f}"
                }
                
                target_sem_courses = []
                
                # Find the semester in history
                # Assuming semester_id matches
                for sem in academic_history.semesters:
                    if sem.semester_id == semester_id:
                        student_info["sgpa"] = f"{sem.sgpa:.2f}" if sem.sgpa is not None else "N/A"
                        
                        # Convert schema courses to dicts for PDF generator
                        for course in sem.courses:
                             target_sem_courses.append({
                                "code": course.code,
                                "name": course.name,
                                "credits": course.credits,
                                "grade": course.course_grade or "N/A"
                             })
                        break
                
                pdf_bytes = pdf_generator.generate_grade_card(student_info, semester_data, target_sem_courses)
                files[f"{student_id}_GradeCard.pdf"] = pdf_bytes
                
            except Exception as e:
                print(f"Error generating for {student_id}: {e}")
                # Log usage
            
            # Update Progress
            tasks[task_id]["progress"] = int(((i + 1) / total) * 100)

        # Create Zip
        zip_bytes = pdf_generator.create_zip(files)
        tasks[task_id]["result"] = zip_bytes
        tasks[task_id]["status"] = "completed"
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


def process_transcripts(task_id: str, student_ids: List[str], db: Session):
    try:
        tasks[task_id]["status"] = "processing"
        total = len(student_ids)
        files = {}
        
        for i, student_id in enumerate(student_ids):
            try:
                from app.services.academic import get_student_academic_history
                # Fetch Academic History using Service
                academic_history = get_student_academic_history(db, student_id)
                if not academic_history: continue
                
                student_info = {
                    "id": academic_history.student_id,
                    "name": academic_history.student_name,
                    "discipline_name": academic_history.discipline_name or "N/A",
                    "cgpa": f"{academic_history.cgpa:.2f}"
                }
                
                semester_history = []
                for sem in academic_history.semesters:
                    sem_courses = []
                    for course in sem.courses:
                        sem_courses.append({
                            "code": course.code,
                            "name": course.name,
                            "credits": course.credits,
                            "grade": course.course_grade or "N/A"
                        })
                    
                    semester_history.append({
                        "name": sem.semester_name,
                        "sgpa": f"{sem.sgpa:.2f}" if sem.sgpa is not None else "N/A",
                        "courses": sem_courses
                    })
                
                pdf_bytes = pdf_generator.generate_transcript(student_info, semester_history)
                files[f"{student_id}_Transcript.pdf"] = pdf_bytes
                
            except Exception as e:
                print(f"Error generating transcript for {student_id}: {e}")

            tasks[task_id]["progress"] = int(((i + 1) / total) * 100)

        zip_bytes = pdf_generator.create_zip(files)
        tasks[task_id]["result"] = zip_bytes
        tasks[task_id]["status"] = "completed"

    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@router.get("/students", response_model=Any)
def get_students_report(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 20,
    search: Optional[str] = None,
    sort_by: Optional[str] = "id",
    sort_desc: bool = False,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Get students report data with filtering and sorting.
    """
    query = db.query(User).filter(User.roles.any(role=UserRole.STUDENT) | User.roles.any(role=UserRole.ALUMNI))
    
    if search:
        search_filter = (
            User.name.ilike(f"%{search}%") | 
            User.id.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
        
    # Validation for sorting to prevent injection/errors
    valid_sort_fields = ['id', 'name', 'created_at', 'discipline_code']
    if sort_by not in valid_sort_fields:
        sort_by = 'id'
        
    sort_attr = getattr(User, sort_by)
    if sort_desc:
        query = query.order_by(sort_attr.desc())
    else:
        query = query.order_by(sort_attr.asc())
        
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": [UserSchema.from_orm(u) for u in users]
    }

@router.post("/generate-grade-cards")
def generate_grade_cards(
    request: GradeCardRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    task_id = str(uuid4())
    tasks[task_id] = {"status": "pending", "progress": 0, "result": None}
    background_tasks.add_task(process_grade_cards, task_id, request.student_ids, request.semester_id, db)
    return {"task_id": task_id}

@router.post("/generate-transcripts")
def generate_transcripts(
    request: TranscriptRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    task_id = str(uuid4())
    tasks[task_id] = {"status": "pending", "progress": 0, "result": None}
    background_tasks.add_task(process_transcripts, task_id, request.student_ids, db)
    return {"task_id": task_id}

@router.get("/tasks/{task_id}")
def get_task_status(
    task_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Don't send large result bytes in status check
    response = {
        "status": task["status"],
        "progress": task["progress"],
        "error": task.get("error")
    }
    return response

from fastapi.responses import Response

@router.get("/tasks/{task_id}/download")
def download_task_result(
    task_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    task = tasks.get(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not ready or found")
        
    return Response(
        content=task["result"],
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=report_{task_id}.zip"}
    )
