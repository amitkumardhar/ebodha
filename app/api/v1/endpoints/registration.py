
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from app.api import deps
from app.models.examination import Registration, GradeMapping
from app.models.course import CourseOffering
from app.models.user import User, UserRole
from app.schemas.examination import Registration as RegistrationSchema, RegistrationCreate, RegistrationUpdate

router = APIRouter()

@router.post("/", response_model=RegistrationSchema)
def create_registration(
    *,
    db: Session = Depends(deps.get_db),
    registration_in: RegistrationCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Register for a course.
    """
    # Students can only register themselves
    if current_user.current_role == UserRole.STUDENT and current_user.id != registration_in.student_id:
         raise HTTPException(status_code=400, detail="Cannot register for another student")
    
    # Check if offering exists
    offering = db.query(CourseOffering).filter(CourseOffering.id == registration_in.course_offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    # Check if already registered
    existing = db.query(Registration).filter(
        Registration.student_id == registration_in.student_id,
        Registration.course_offering_id == registration_in.course_offering_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this course")

    registration = Registration(**registration_in.dict())
    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

@router.get("/me", response_model=List[RegistrationSchema])
def read_my_registrations(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's registrations.
    """
    registrations = db.query(Registration).filter(Registration.student_id == current_user.id).all()
    return registrations

@router.post("/bulk-upload")
async def bulk_upload_registrations(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Bulk upload registrations from CSV.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    # Validate headers
    # We expect 'student_id', 'course_code', and 'semester'
    fieldnames = csv_reader.fieldnames
    if not fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
        
    required_fields = {'student_id', 'course_code'}
    if not required_fields.issubset(set(fieldnames)):
         missing = required_fields - set(fieldnames)
         raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")
    
    if 'semester' not in fieldnames:
         raise HTTPException(status_code=400, detail="Missing required column: semester")
    
    registrations_created = 0
    errors = []
    
    from app.models.academic import Semester
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get('student_id', '').strip() if row.get('student_id', '') else None
            course_code = row.get('course_code', '').strip() if row.get('course_code', '') else None
            
            semester_id = None
            semester_name = row.get('semester', '').strip() if row.get('semester', '') else None
            
            if not student_id or not course_code:
                errors.append(f"Row {row_idx}: Missing required fields")
                continue
                
            # Resolve Semester ID
            if semester_name:
                semester = db.query(Semester).filter(Semester.name == semester_name).first()
                if not semester:
                    errors.append(f"Row {row_idx}: Semester '{semester_name}' not found")
                    continue
                semester_id = semester.id
            else:
                errors.append(f"Row {row_idx}: Missing semester info")
                continue
            
            # Find offering
            offering = db.query(CourseOffering).filter(
                CourseOffering.course_code == course_code,
                CourseOffering.semester_id == semester_id
            ).first()
            
            if not offering:
                errors.append(f"Row {row_idx}: Course offering not found for {course_code} in semester {semester_id}")
                continue
            
            # Check existing
            existing = db.query(Registration).filter(
                Registration.student_id == student_id,
                Registration.course_offering_id == offering.id
            ).first()
            
            if not existing:
                reg = Registration(student_id=student_id, course_offering_id=offering.id)
                db.add(reg)
                registrations_created += 1
                
        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "registrations_created": registrations_created,
        "errors": errors
    }

@router.put("/{registration_id}/grade", response_model=RegistrationSchema)
def assign_grade(
    *,
    db: Session = Depends(deps.get_db),
    registration_id: int,
    grade_in: RegistrationUpdate,
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Assign grade to a registration.
    """
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Verify teacher teaches this course (or is admin)
    # TODO: Add check if current_user is teacher of this course offering
    
    if grade_in.grade:
        registration.grade = grade_in.grade
        # Auto calculate grade point
        mapping = db.query(GradeMapping).filter(GradeMapping.grade == grade_in.grade).first()
        if mapping:
            registration.grade_point = mapping.points
        else:
             raise HTTPException(status_code=400, detail=f"Grade mapping not found for grade {grade_in.grade}")

    db.add(registration)
    db.commit()
    db.refresh(registration)
    return registration

@router.delete("/{registration_id}")
def delete_registration(
    *,
    db: Session = Depends(deps.get_db),
    registration_id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a registration and its associated marks.
    """
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Delete associated marks
    # Note: We need to import Marks if not already imported or use relationship cascade
    # Let's use the relationship if available, or manual query.
    # checking imports: from app.models.examination import Registration, GradeMapping
    # We need Marks. It is in app.models.examination.
    from app.models.examination import Marks
    
    db.query(Marks).filter(Marks.registration_id == registration_id).delete()
    
    db.delete(registration)
    db.commit()
    return {"message": "Registration deleted successfully"}

@router.post("/bulk-upload-grades")
async def bulk_upload_grades(
    course_code: str,
    semester_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Bulk upload grades from CSV.
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
    
    grades_updated = 0
    errors = []
    
    # Cache mappings
    mappings = {m.grade: m.points for m in db.query(GradeMapping).all()}
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get('student_id')
            grade = row.get('grade')
            
            if not student_id or not grade:
                errors.append(f"Row {row_idx}: Missing student_id or grade")
                continue
            
            if grade not in mappings:
                errors.append(f"Row {row_idx}: Invalid grade {grade}")
                continue
                
            registration = db.query(Registration).filter(
                Registration.student_id == student_id,
                Registration.course_offering_id == offering.id
            ).first()
            
            if registration:
                registration.grade = grade
                registration.grade_point = mappings[grade]
                db.add(registration)
                grades_updated += 1
            else:
                errors.append(f"Row {row_idx}: Registration not found for student {student_id}")

        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "grades_updated": grades_updated,
        "errors": errors
    }

from app.schemas.report import StudentGradeReportItem, ExamMarksReport, CourseInfo

@router.get("/my-report", response_model=List[StudentGradeReportItem])
def get_my_report(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get comprehensive grade report for the current student.
    """
    if current_user.current_role != UserRole.STUDENT and current_user.current_role != UserRole.ALUMNI:
         # Allow alumni too? Requirement says "students", but alumni usually want transcripts.
         # Let's restrict to student/alumni.
         pass
         
    registrations = db.query(Registration).filter(Registration.student_id == current_user.id).all()
    
    report = []
    for reg in registrations:
        # Format credits
        c = reg.course_offering.course
        credits_str = f"{c.lecture_credits}-{c.tutorial_credits}-{c.practice_credits}"
        
        course_info = CourseInfo(
            code=c.code,
            name=c.name,
            semester_id=reg.course_offering.semester_id,
            credits=credits_str
        )
        
        # Get Marks
        marks_list = []
        for m in reg.marks:
            marks_list.append(ExamMarksReport(
                examination_id=m.examination_id,
                exam_name=m.examination.name,
                max_marks=m.examination.max_marks,
                marks_obtained=m.marks_obtained
            ))
        
        # Sort marks by examination_id
        marks_list.sort(key=lambda x: x.examination_id)
            
        # Get Compartment Grade
        compartment_reg = db.query(CompartmentRegistration).filter(
            CompartmentRegistration.student_id == current_user.id,
            CompartmentRegistration.course_offering_id == reg.course_offering_id
        ).first()
        
        compartment_grade = compartment_reg.grade if compartment_reg else None
            
        report.append(StudentGradeReportItem(
            course=course_info,
            grade=reg.grade,
            grade_point=reg.grade_point,
            compartment_grade=compartment_grade,
            marks=marks_list
        ))
        
    return report

from app.schemas.examination import CompartmentRegistrationCreate, CompartmentRegistration as CompartmentRegistrationSchema, CompartmentGradeUpdate, CompartmentStudentDetails
from app.models.examination import Compartment as CompartmentRegistration

@router.get("/compartment/details", response_model=List[CompartmentStudentDetails])
def read_compartment_details(
    semester_id: int,
    course_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve students registered for compartment exam for a specific course offering.
    """
    if current_user.current_role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this endpoint"
        )
        
    offering = db.query(CourseOffering).filter(
        CourseOffering.semester_id == semester_id,
        CourseOffering.course_code == course_code
    ).first()
    
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
        
    # Check permissions for Teacher
    if current_user.current_role == UserRole.TEACHER:
        # Check if teacher teaches this course
        # Note: We need TeacherCourse model import for this check if we want to be strict.
        # Assuming admin handles compartment mostly, but let's be safe.
        # Importing locally to avoid circulars if any, though model imports are usually fine.
        from app.models.course import TeacherCourse
        is_assigned = db.query(TeacherCourse).filter(
            TeacherCourse.teacher_id == current_user.id,
            TeacherCourse.course_offering_id == offering.id
        ).first()
        if not is_assigned:
             raise HTTPException(
                status_code=403, detail="Not authorized to view details for this course"
            )

    compartment_regs = db.query(CompartmentRegistration).filter(
        CompartmentRegistration.course_offering_id == offering.id
    ).all()
    
    results = []
    for comp in compartment_regs:
        # Get original grade from Registration
        reg = db.query(Registration).filter(
            Registration.student_id == comp.student_id,
            Registration.course_offering_id == offering.id
        ).first()
        
        results.append(CompartmentStudentDetails(
            id=comp.id,
            student_id=comp.student_id,
            student_name=comp.student.name if comp.student else "Unknown",
            grade=comp.grade,
            grade_point=comp.grade_point,
            original_grade=reg.grade if reg else None
        ))
        
    return results

@router.post("/compartment", response_model=CompartmentRegistrationSchema)
def register_compartment(
    *,
    db: Session = Depends(deps.get_db),
    registration_in: CompartmentRegistrationCreate,
    current_user: User = Depends(deps.get_current_active_admin), # Or teacher? Usually admin/student. Let's say admin for now as per "registering students"
) -> Any:
    """
    Register a student for compartment examination.
    """
    # Verify student is registered for the course
    reg = db.query(Registration).filter(
        Registration.student_id == registration_in.student_id,
        Registration.course_offering_id == registration_in.course_offering_id
    ).first()
    
    if not reg:
        raise HTTPException(status_code=400, detail="Student is not registered for this course offering")
        
    # Check if already registered for compartment
    existing = db.query(CompartmentRegistration).filter(
        CompartmentRegistration.student_id == registration_in.student_id,
        CompartmentRegistration.course_offering_id == registration_in.course_offering_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Student already registered for compartment exam")
        
    compartment_reg = CompartmentRegistration(
        student_id=registration_in.student_id,
        course_offering_id=registration_in.course_offering_id
    )
    db.add(compartment_reg)
    db.commit()
    db.refresh(compartment_reg)
    return compartment_reg

@router.post("/compartment/bulk", response_model=Any)
def bulk_register_compartment(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Bulk register students for compartment examination via CSV.
    CSV Format: student_id, course_offering_id
    """
    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(contents))
    
    # Validate headers
    fieldnames = csv_reader.fieldnames
    if not fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
    
    required_fields = {'student_id', 'course_code'}
    if not required_fields.issubset(set(fieldnames)):
         missing = required_fields - set(fieldnames)
         raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")
    
    if 'semester' not in fieldnames:
         raise HTTPException(status_code=400, detail="Missing required column: semester")

    registered_count = 0
    errors = []
    
    from app.models.academic import Semester
    from app.models.course import CourseOffering
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get("student_id", "").strip() if row.get("student_id", "") else None
            course_code = row.get("course_code", "").strip() if row.get("course_code", "") else None
            semester_name = row.get("semester", "").strip() if row.get("semester", "") else None
            
            if not student_id or not course_code or not semester_name:
                errors.append(f"Row {row_idx}: Missing required fields")
                continue
            
            # Lookup semester
            semester = db.query(Semester).filter(Semester.name == semester_name).first()
            if not semester:
                errors.append(f"Row {row_idx}: Semester '{semester_name}' not found")
                continue
            
            # Lookup offering
            offering = db.query(CourseOffering).filter(
                CourseOffering.course_code == course_code,
                CourseOffering.semester_id == semester.id
            ).first()
            
            if not offering:
                errors.append(f"Row {row_idx}: Course offering not found for {course_code} in semester {semester_name}")
                continue
            
            course_offering_id = offering.id
            
            # Verify registration
            reg = db.query(Registration).filter(
                Registration.student_id == student_id,
                Registration.course_offering_id == course_offering_id
            ).first()
            
            if not reg:
                errors.append(f"Row {row_idx}: Student {student_id} not registered for course {course_code}")
                continue
                
            # Check existing
            existing = db.query(CompartmentRegistration).filter(
                CompartmentRegistration.student_id == student_id,
                CompartmentRegistration.course_offering_id == course_offering_id
            ).first()
            
            if existing:
                errors.append(f"Row {row_idx}: Student {student_id} already registered for compartment in {course_code}")
                continue
                
            compartment_reg = CompartmentRegistration(
                student_id=student_id,
                course_offering_id=course_offering_id
            )
            db.add(compartment_reg)
            registered_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "registered_count": registered_count,
        "errors": errors
    }

@router.put("/compartment/{compartment_id}/grade", response_model=CompartmentRegistrationSchema)
def update_compartment_grade(
    *,
    db: Session = Depends(deps.get_db),
    compartment_id: int,
    grade_in: CompartmentGradeUpdate,
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Update grade for a compartment registration.
    """
    compartment_reg = db.query(CompartmentRegistration).filter(CompartmentRegistration.id == compartment_id).first()
    if not compartment_reg:
        raise HTTPException(status_code=404, detail="Compartment registration not found")
        
    compartment_reg.grade = grade_in.grade
    
    # Auto calculate grade point
    mapping = db.query(GradeMapping).filter(GradeMapping.grade == grade_in.grade).first()
    if mapping:
        compartment_reg.grade_point = mapping.points
    else:
         raise HTTPException(status_code=400, detail=f"Grade mapping not found for grade {grade_in.grade}")
         
    db.add(compartment_reg)
    db.commit()
    db.refresh(compartment_reg)
    return compartment_reg

@router.post("/compartment/bulk-grades", response_model=Any)
def bulk_upload_compartment_grades(
    course_code: str,
    semester_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Bulk upload grades for compartment examination via CSV.
    CSV Format: student_id, grade
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

    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(contents))
    
    # Validate headers
    fieldnames = csv_reader.fieldnames
    if not fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
        
    required_fields = {'student_id', 'grade'}
    if not required_fields.issubset(set(fieldnames)):
         missing = required_fields - set(fieldnames)
         raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")
    
    updated_count = 0
    errors = []
    
    # Cache mappings
    mappings = {m.grade: m.points for m in db.query(GradeMapping).all()}
    
    for row_idx, row in enumerate(csv_reader):
        try:
            student_id = row.get("student_id", "").strip()
            grade = row.get("grade", "").strip()
            
            if not student_id or not grade:
                errors.append(f"Row {row_idx}: Missing student_id or grade")
                continue
            
            # Find compartment registration using offering Context
            compartment_reg = db.query(CompartmentRegistration).filter(
                CompartmentRegistration.student_id == student_id,
                CompartmentRegistration.course_offering_id == offering.id
            ).first()
            
            if not compartment_reg:
                errors.append(f"Row {row_idx}: Compartment registration not found for student {student_id}")
                continue
            
            if grade not in mappings:
                errors.append(f"Row {row_idx}: Invalid grade {grade} for student {student_id}")
                continue
                
            compartment_reg.grade = grade
            compartment_reg.grade_point = mappings[grade]
            db.add(compartment_reg)
            updated_count += 1
            
        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "updated_count": updated_count,
        "errors": errors
    }
