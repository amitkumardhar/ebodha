
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import csv
import io

from app.api import deps
from app.models.course import Course, CourseOffering, TeacherCourse, CourseCategory
from app.models.examination import Examination
from app.models.user import User, UserRole
from app.schemas.course import Course as CourseSchema, CourseCreate, CourseOffering as CourseOfferingSchema, CourseOfferingCreate

router = APIRouter()

@router.get("/", response_model=List[CourseSchema])
def read_courses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve courses.
    """
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.post("/", response_model=CourseSchema)
def create_course(
    *,
    db: Session = Depends(deps.get_db),
    course_in: CourseCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new course.
    """
    course = db.query(Course).filter(Course.code == course_in.code).first()
    if course:
        raise HTTPException(status_code=400, detail="Course already exists")
    course = Course(**course_in.dict())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.get("/semester-courses", response_model=List[CourseOfferingSchema])
def read_semester_courses(
    semester_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve courses for a semester based on user role.
    Teachers see only their courses. Admins see all courses.
    """
    if current_user.current_role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this endpoint"
        )

    if current_user.current_role == UserRole.ADMIN:
        offerings = db.query(CourseOffering).filter(CourseOffering.semester_id == semester_id).all()
    else:
        # Teacher
        offerings = (
            db.query(CourseOffering)
            .join(TeacherCourse)
            .filter(
                CourseOffering.semester_id == semester_id,
                TeacherCourse.teacher_id == current_user.id
            )
            .all()
        )
    return offerings

from app.schemas.course import StudentCourseDetails
from app.models.examination import Registration, Compartment
from app.schemas.report import ExamMarksReport

@router.get("/semester-course-details", response_model=List[StudentCourseDetails])
def read_semester_course_details(
    semester_id: int,
    course_code: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve student details, grades, and marks for a specific course offering.
    Teachers see only courses they are assigned to. Admins see all.
    """
    if current_user.current_role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this endpoint"
        )

    # Find offering
    offering = db.query(CourseOffering).filter(
        CourseOffering.semester_id == semester_id,
        CourseOffering.course_code == course_code
    ).first()

    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")

    # Check permissions for Teacher
    if current_user.current_role == UserRole.TEACHER:
        is_assigned = db.query(TeacherCourse).filter(
            TeacherCourse.teacher_id == current_user.id,
            TeacherCourse.course_offering_id == offering.id
        ).first()
        if not is_assigned:
             raise HTTPException(
                status_code=403, detail="Not authorized to view details for this course"
            )

    # Fetch registrations
    registrations = db.query(Registration).filter(
        Registration.course_offering_id == offering.id
    ).all()

    results = []
    for reg in registrations:
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
        
        # Compartment details
        comp_reg = db.query(Compartment).filter(
            Compartment.student_id == reg.student_id,
            Compartment.course_offering_id == offering.id
        ).first()
        
        compartment_grade = comp_reg.grade if comp_reg else None
        compartment_registration_id = comp_reg.id if comp_reg else None
        
        # Calculate Course Grade (better of original and compartment)
        course_grade = reg.grade
        if compartment_grade:
            reg_gp = reg.grade_point if reg.grade_point is not None else -1.0
            comp_gp = comp_reg.grade_point if comp_reg.grade_point is not None else -1.0
            if comp_gp > reg_gp:
                course_grade = compartment_grade

        results.append(StudentCourseDetails(
            registration_id=reg.id,
            student_id=reg.student_id,
            student_name=reg.student.name,
            grade=reg.grade,
            grade_point=reg.grade_point,
            compartment_grade=compartment_grade,
            course_grade=course_grade,
            compartment_registration_id=compartment_registration_id,
            marks=marks_list
        ))
        
    return results

@router.get("/offerings/", response_model=List[CourseOfferingSchema])
def read_course_offerings(
    semester_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve course offerings for a semester.
    """
    offerings = db.query(CourseOffering).filter(CourseOffering.semester_id == semester_id).all()
    return offerings
            # Check/Create Course


@router.post("/offerings/", response_model=CourseOfferingSchema)
def create_course_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_in: CourseOfferingCreate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new course offering.
    """
    offering = CourseOffering(**offering_in.dict())
    db.add(offering)
    db.commit()
    db.refresh(offering)
    return offering

from app.schemas.course import CourseOfferingUpdate

@router.put("/offerings/{offering_id}", response_model=CourseOfferingSchema)
def update_course_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_id: int,
    offering_in: CourseOfferingUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a course offering.
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
    
    update_data = offering_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offering, field, value)
        
    db.add(offering)
    db.commit()
    db.refresh(offering)
    return offering

@router.delete("/offerings/{offering_id}")
def delete_course_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a course offering.
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
    
    # Check for dependencies (registrations, examinations, teachers)
    if offering.registrations or offering.examinations or offering.teachers:
        raise HTTPException(status_code=400, detail="Cannot delete course offering with existing registrations or exams")
        
    db.delete(offering)
    db.commit()
    return {"message": "Course offering deleted successfully"}

@router.post("/offerings/bulk-upload")
async def bulk_upload_course_offerings(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Bulk upload course offerings from CSV.
    CSV Format: course_code, semester_id, course_name, category, credits, teacher_ids   
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    # Get all column headers
    fieldnames = csv_reader.fieldnames
    if not fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
    
    # Validate headers
    required_fields = {'course_code','semester'}
    if not required_fields.issubset(set(fieldnames)):
         missing = required_fields - set(fieldnames)
         raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")
    
    # Identify exam columns (all columns except known reserved columns)
    reserved_columns = {'course_code', 'semester', 'course_name', 'category', 'credits', 'teacher_ids'}
    exam_columns = [col for col in fieldnames if col not in reserved_columns]
    
    courses_created = 0
    offerings_created = 0
    exams_created = 0
    errors = []
    
    from app.models.academic import Semester
    
    for row_idx, row in enumerate(csv_reader):
        try:
            course_code = row.get('course_code', '').strip() if row.get('course_code', '') else None
            semester_name = row.get('semester', '').strip() if row.get('semester', '') else None   
            course_name = row.get('course_name', '').strip() if row.get('course_name', '') else None
            category_str = row.get('category', '').strip() if row.get('category', '') else None
            credits_str = row.get('credits', '').strip() if row.get('credits', '') else None
            teacher_ids_str = row.get('teacher_ids', '').strip() if row.get('teacher_ids', '') else None
            
            if not course_code or not semester_name:
                errors.append(f"Row {row_idx}: Missing course_code or semester")
                continue

            # Lookup semester
            semester = db.query(Semester).filter(Semester.name == semester_name).first()
            if not semester:
                errors.append(f"Row {row_idx}: Semester '{semester_name}' not found")
                continue
            semester_id = semester.id
            
            # Check/Create Course
            course = db.query(Course).filter(Course.code == course_code).first()
            if not course:
                # Create course if details provided
                if course_name and category_str:
                     # Parse credits L-T-P
                    l, t, p = 0, 0, 0
                    if credits_str:
                        parts = credits_str.split('-')
                        if len(parts) == 3:
                            l, t, p = map(int, parts)
                    
                    course = Course(
                        code=course_code,
                        name=course_name,
                        category=CourseCategory(category_str),
                        lecture_credits=l,
                        tutorial_credits=t,
                        practice_credits=p
                    )
                    db.add(course)
                    db.flush() # Flush to get it in session but not commit yet
                    courses_created += 1
                else:
                    errors.append(f"Row {row_idx}: Course {course_code} not found and details not provided")
                    continue
            
            # Create Offering if it does not exist
            offering = db.query(CourseOffering).filter(
                CourseOffering.course_code == course_code,
                CourseOffering.semester_id == semester_id
            ).first()
            
            if not offering:
                offering = CourseOffering(course_code=course_code, semester_id=semester_id)
                db.add(offering)
                db.flush()
                offerings_created += 1
            
            # Assign Teachers
            if teacher_ids_str:
                teacher_ids = teacher_ids_str.split(';')
                for tid in teacher_ids:
                    tid = tid.strip()
                    if not tid: continue
                    # Check if teacher exists
                    teacher = db.query(User).filter(User.id == tid).first() # Assuming User ID is used
                    if teacher:
                        # Check if already assigned
                        exists = db.query(TeacherCourse).filter(
                            TeacherCourse.teacher_id == tid,
                            TeacherCourse.course_offering_id == offering.id
                        ).first()
                        if not exists:
                            tc = TeacherCourse(teacher_id=tid, course_offering_id=offering.id)
                            db.add(tc)
            
            # Process exam columns
            for exam_name in exam_columns:
                max_marks_str = row.get(exam_name, '').strip() if row.get(exam_name, '') else None
                
                # Skip if empty or zero
                if not max_marks_str or max_marks_str == '0':
                    continue
                
                try:
                    max_marks = float(max_marks_str)
                    if max_marks <= 0:
                        continue
                except ValueError:
                    errors.append(f"Row {row_idx}: Invalid max_marks '{max_marks_str}' for exam '{exam_name}'")
                    continue
                
                # Check if exam already exists
                exam = db.query(Examination).filter(
                    Examination.course_offering_id == offering.id,
                    Examination.name == exam_name
                ).first()
                
                if not exam:
                    exam = Examination(
                        course_offering_id=offering.id,
                        name=exam_name,
                        max_marks=max_marks
                    )
                    db.add(exam)
                    exams_created += 1
                else:
                    # Update max_marks if exam already exists
                    exam.max_marks = max_marks

        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
    
    db.commit()
    
    return {
        "courses_created": courses_created,
        "offerings_created": offerings_created,
        "exams_created": exams_created,
        "errors": errors
    }

from app.schemas.teacher import TeacherCourse as TeacherCourseSchema, TeacherCourseCreate, TeacherInfo

@router.post("/offerings/{offering_id}/teachers", response_model=TeacherCourseSchema)
def assign_teacher_to_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_id: int,
    teacher_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Assign a teacher to a course offering.
    """
    # Check if offering exists
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
    
    # Check if teacher exists
    teacher = db.query(User).filter(User.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    # Check if already assigned
    existing = db.query(TeacherCourse).filter(
        TeacherCourse.teacher_id == teacher_id,
        TeacherCourse.course_offering_id == offering_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Teacher already assigned to this course offering")
    
    teacher_course = TeacherCourse(teacher_id=teacher_id, course_offering_id=offering_id)
    db.add(teacher_course)
    db.commit()
    db.refresh(teacher_course)
    return teacher_course

@router.delete("/offerings/{offering_id}/teachers/{teacher_id}")
def remove_teacher_from_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_id: int,
    teacher_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Remove a teacher from a course offering.
    """
    teacher_course = db.query(TeacherCourse).filter(
        TeacherCourse.teacher_id == teacher_id,
        TeacherCourse.course_offering_id == offering_id
    ).first()
    
    if not teacher_course:
        raise HTTPException(status_code=404, detail="Teacher assignment not found")
    
    db.delete(teacher_course)
    db.commit()
    return {"message": "Teacher removed from course offering"}

@router.get("/offerings/{offering_id}/teachers", response_model=List[TeacherInfo])
def list_teachers_for_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    List all teachers assigned to a course offering.
    """
    offering = db.query(CourseOffering).filter(CourseOffering.id == offering_id).first()
    if not offering:
        raise HTTPException(status_code=404, detail="Course offering not found")
    
    teacher_assignments = db.query(TeacherCourse).filter(
        TeacherCourse.course_offering_id == offering_id
    ).all()
    
    results = []
    for tc in teacher_assignments:
        results.append(TeacherInfo(
            id=tc.id,
            teacher_id=tc.teacher_id,
            teacher_name=tc.teacher.name
        ))
    
    return results

from app.schemas.course import CourseUpdate

@router.put("/{course_code}", response_model=CourseSchema)
def update_course(
    *,
    db: Session = Depends(deps.get_db),
    course_code: str,
    course_in: CourseUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a course.
    """
    course = db.query(Course).filter(Course.code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    update_data = course_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
        
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

@router.delete("/{course_code}")
def delete_course(
    *,
    db: Session = Depends(deps.get_db),
    course_code: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a course.
    """
    course = db.query(Course).filter(Course.code == course_code).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Check for dependencies (offerings)
    offerings = db.query(CourseOffering).filter(CourseOffering.course_code == course_code).first()
    if offerings:
        raise HTTPException(status_code=400, detail="Cannot delete course with existing offerings")
        
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}