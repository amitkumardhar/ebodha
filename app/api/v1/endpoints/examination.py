
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from app.api import deps
from app.models.examination import Examination, Marks, Registration
from app.models.course import CourseOffering
from app.models.user import User, UserRole
from app.schemas.examination import Examination as ExaminationSchema, ExaminationCreate

router = APIRouter()

@router.post("/", response_model=ExaminationSchema)
def create_examination(
    *,
    db: Session = Depends(deps.get_db),
    exam_in: ExaminationCreate,
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Create new examination.
    """
    exam = Examination(**exam_in.dict())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

@router.post("/bulk-upload-marks")
async def bulk_upload_marks(
    course_code: str,
    semester_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Bulk upload marks from CSV.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    # Verify offering
    offering = db.query(CourseOffering).filter(
        CourseOffering.course_code == course_code,
        CourseOffering.semester_id == semester_id
    ).first()
    
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    marks_updated = 0
    exams_processed = set()
    errors = []
    
    # Get all exams for this offering
    existing_exams = {e.name: e for e in db.query(Examination).filter(Examination.course_offering_id == offering.id).all()}
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get('student_id')
            if not student_id:
                errors.append(f"Row {row_idx}: Missing student_id")
                continue
            
            registration = db.query(Registration).filter(
                Registration.student_id == student_id,
                Registration.course_offering_id == offering.id
            ).first()
            
            if not registration:
                errors.append(f"Row {row_idx}: Registration not found for student {student_id}")
                continue

            for key, value in row.items():
                if key == 'student_id': continue
                
                exam_name = key
                try:
                    marks_obtained = float(value)
                except ValueError:
                    errors.append(f"Row {row_idx}: Invalid marks for {exam_name}")
                    continue
                
                if exam_name not in existing_exams:
                    # Auto create exam? Or error? Let's error for now as per strict design, or maybe auto-create if we want flexibility.
                    # Design didn't specify auto-create exams on marks upload, but it's handy.
                    # Let's assume exams must exist.
                    errors.append(f"Row {row_idx}: Examination {exam_name} not found")
                    continue
                
                exam = existing_exams[exam_name]
                exams_processed.add(exam_name)
                
                # Update/Create Marks
                marks = db.query(Marks).filter(
                    Marks.registration_id == registration.id,
                    Marks.examination_id == exam.id
                ).first()
                
                if marks:
                    marks.marks_obtained = marks_obtained
                else:
                    marks = Marks(
                        registration_id=registration.id,
                        examination_id=exam.id,
                        marks_obtained=marks_obtained
                    )
                    db.add(marks)
                marks_updated += 1

        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "marks_updated": marks_updated,
        "exams_processed": list(exams_processed),
        "errors": errors
    }
