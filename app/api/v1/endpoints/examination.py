
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

from app.schemas.examination import ExaminationUpdate

@router.put("/{exam_id}", response_model=ExaminationSchema)
def update_examination(
    *,
    db: Session = Depends(deps.get_db),
    exam_id: int,
    exam_in: ExaminationUpdate,
    current_user: User = Depends(deps.get_current_active_teacher), # Teachers/Admins
) -> Any:
    """
    Update an examination.
    """
    exam = db.query(Examination).filter(Examination.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")
    
    update_data = exam_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)
        
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam

@router.delete("/{exam_id}")
def delete_examination(
    *,
    db: Session = Depends(deps.get_db),
    exam_id: int,
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Delete an examination.
    """
    exam = db.query(Examination).filter(Examination.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")
    
    # Check for marks
    if exam.marks:
        raise HTTPException(status_code=400, detail="Cannot delete examination with existing marks")
        
    db.delete(exam)
    db.commit()
    return {"message": "Examination deleted successfully"}

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
    
    # Validate headers
    fieldnames = csv_reader.fieldnames
    if not fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
    
    if 'student_id' not in fieldnames:
        raise HTTPException(status_code=400, detail="Missing required column: student_id")
    
    marks_updated = 0
    exams_processed = set()
    errors = []
    
    # Get all exams for this offering
    existing_exams = {e.name: e for e in db.query(Examination).filter(Examination.course_offering_id == offering.id).all()}
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get('student_id', '').strip() if row.get('student_id', '') else None
            if not student_id:
                errors.append(f"Row {row_idx}: Missing student_id")
                continue
            
            # Check registration only if student_id is present
            registration = db.query(Registration).filter(
                Registration.student_id == student_id,
                Registration.course_offering_id == offering.id
            ).first()
            
            if not registration:
                errors.append(f"Row {row_idx}: Registration not found for student {student_id}")
                continue

            for key, value in row.items():
                if key == 'student_id' or not key: 
                    continue
                
                exam_name = key.strip()
                val_str = value.strip() if value else ''
                
                if not val_str:
                    continue # Skip empty values
                    
                try:
                    marks_obtained = float(val_str)
                except ValueError:
                    errors.append(f"Row {row_idx}: Invalid marks '{val_str}' for {exam_name}")
                    continue
                
                if exam_name not in existing_exams:
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

from app.schemas.examination import MarkUpdate

@router.put("/marks", response_model=Any)
def update_marks(
    *,
    db: Session = Depends(deps.get_db),
    mark_in: MarkUpdate,
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Update marks for a specific student and exam.
    """
    # Verify offering
    offering = db.query(CourseOffering).filter(
        CourseOffering.course_code == mark_in.course_code,
        CourseOffering.semester_id == mark_in.semester_id
    ).first()
    
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
        
    # Verify registration
    registration = db.query(Registration).filter(
        Registration.student_id == mark_in.student_id,
        Registration.course_offering_id == offering.id
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
        
    # Verify examination
    exam = db.query(Examination).filter(
        Examination.course_offering_id == offering.id,
        Examination.name == mark_in.exam_name
    ).first()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Examination not found")
        
    # Update/Create Marks
    marks = db.query(Marks).filter(
        Marks.registration_id == registration.id,
        Marks.examination_id == exam.id
    ).first()
    
    if marks:
        marks.marks_obtained = mark_in.marks
    else:
        marks = Marks(
            registration_id=registration.id,
            examination_id=exam.id,
            marks_obtained=mark_in.marks
        )
        db.add(marks)
        
    db.commit()
    
    return {"message": "Marks updated successfully"}
