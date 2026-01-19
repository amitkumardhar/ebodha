
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
from app.models.examination import Registration
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
                exam_name=m.examination.name,
                max_marks=m.examination.max_marks,
                marks_obtained=m.marks_obtained
            ))
        
        results.append(StudentCourseDetails(
            registration_id=reg.id,
            student_id=reg.student_id,
            student_name=reg.student.name,
            grade=reg.grade,
            grade_point=reg.grade_point,
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

@router.post("/offerings/bulk-upload")
async def bulk_upload_course_offerings(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Bulk upload course offerings from CSV.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    courses_created = 0
    offerings_created = 0
    errors = []
    
    for row_idx, row in enumerate(csv_reader):
        try:
            course_code = row.get('course_code')
            semester_id = int(row.get('semester_id'))
            
            if not course_code or not semester_id:
                errors.append(f"Row {row_idx}: Missing course_code or semester_id")
                continue

            # Check/Create Course
            course = db.query(Course).filter(Course.code == course_code).first()
            if not course:
                # Create course if details provided
                if 'course_name' in row and 'category' in row:
                     # Parse credits L-T-P
                    l, t, p = 0, 0, 0
                    if 'credits' in row:
                        parts = row['credits'].split('-')
                        if len(parts) == 3:
                            l, t, p = map(int, parts)
                    
                    course = Course(
                        code=course_code,
                        name=row['course_name'],
                        category=CourseCategory(row['category']),
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
            
            # Create Offering
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
            if 'teacher_ids' in row and row['teacher_ids']:
                teacher_ids = row['teacher_ids'].split(';')
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
            
            # Create Exams
            if 'exams' in row and row['exams']:
                exams = row['exams'].split(';')
                for exam_str in exams:
                    if ':' in exam_str:
                        name, max_marks = exam_str.split(':')
                        # Check if exam exists
                        exam = db.query(Examination).filter(
                            Examination.course_offering_id == offering.id,
                            Examination.name == name.strip()
                        ).first()
                        if not exam:
                            exam = Examination(
                                course_offering_id=offering.id,
                                name=name.strip(),
                                max_marks=float(max_marks)
                            )
                            db.add(exam)

        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
    
    db.commit()
    
    return {
        "courses_created": courses_created,
        "offerings_created": offerings_created,
        "errors": errors
    }
