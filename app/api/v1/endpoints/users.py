
from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate
from app.schemas.academic import AcademicHistory, AcademicHistorySemester, AcademicHistoryCourse
from app.models.examination import Registration, Compartment as CompartmentRegistration
from app.models.course import CourseOffering
from app.models.academic import Semester
from app.models.discipline import Discipline

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

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
        discipline_code=user_in.discipline_code,
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

@router.get("/{user_id}/academic-history", response_model=AcademicHistory)
def get_user_academic_history(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_teacher),
) -> Any:
    """
    Get academic history of a student/alumni.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Get all registrations
    registrations = db.query(Registration).filter(Registration.student_id == user_id).all()
    
    # Get all compartment registrations
    compartment_regs = db.query(CompartmentRegistration).filter(CompartmentRegistration.student_id == user_id).all()
    compartment_map = {c.course_offering_id: c for c in compartment_regs}
    
    # Get Discipline Name
    discipline_name = None
    if user.discipline_code:
        discipline = db.query(Discipline).filter(Discipline.code == user.discipline_code).first()
        if discipline:
            discipline_name = discipline.name
    
    # Group by semester
    semesters_map = {}
    
    for reg in registrations:
        offering = reg.course_offering
        semester = offering.semester
        
        if semester.id not in semesters_map:
            semesters_map[semester.id] = {
                "semester_id": semester.id,
                "semester_name": semester.name,
                "start_date": semester.start_date,
                "courses": [],
                "total_credits": 0.0, # Changed to float
                "total_points": 0.0
            }
            
        # Determine grades
        original_grade = reg.grade
        original_points = reg.grade_point
        
        comp_reg = compartment_map.get(offering.id)
        compartment_grade = comp_reg.grade if comp_reg else None
        compartment_points = comp_reg.grade_point if comp_reg else None
        
        effective_grade = compartment_grade if compartment_grade else original_grade
        effective_points = compartment_points if compartment_points is not None else original_points
        
        # Calculate Credits (L + T + 0.5 * P)
        course_credits = float(offering.course.lecture_credits + offering.course.tutorial_credits + (0.5 * offering.course.practice_credits))
        
        course_data = AcademicHistoryCourse(
            code=offering.course.code,
            name=offering.course.name,
            credits=course_credits,
            original_grade=original_grade,
            compartment_grade=compartment_grade,
            course_grade=effective_grade,
            grade_point=effective_points
        )
        
        semesters_map[semester.id]["courses"].append(course_data)
        
        # Add to semester totals if grade is present (passed/failed but graded)
        if effective_points is not None:
             semesters_map[semester.id]["total_credits"] += course_credits
             semesters_map[semester.id]["total_points"] += (effective_points * course_credits)
             
    # Calculate SGPA & CGPA
    # Note: CGPA calculation rules can be complex (e.g. failing grades logic). 
    # Here we assume simple weighted average of all courses taken.
    
    total_credits_cumulative = 0.0
    total_points_cumulative = 0.0
    
    semester_list = []
    
    sorted_semesters = sorted(semesters_map.values(), key=lambda x: x["start_date"], reverse=True)
    
    for sem_data in sorted_semesters:
        sgpa = None
        if sem_data["total_credits"] > 0:
            sgpa = sem_data["total_points"] / sem_data["total_credits"]
            
        total_credits_cumulative += sem_data["total_credits"]
        total_points_cumulative += sem_data["total_points"]
        
        semester_list.append(AcademicHistorySemester(
            semester_id=sem_data["semester_id"],
            semester_name=sem_data["semester_name"],
            start_date=sem_data["start_date"],
            sgpa=round(sgpa, 2) if sgpa is not None else None,
            courses=sem_data["courses"]
        ))
        
    cgpa = None
    if total_credits_cumulative > 0:
        cgpa = total_points_cumulative / total_credits_cumulative
        
    return AcademicHistory(
        student_id=user.id,
        student_name=user.name,
        discipline_code=user.discipline_code,
        discipline_name=discipline_name,
        cgpa=round(cgpa, 2) if cgpa is not None else 0.0,
        semesters=semester_list
    )

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

from fastapi import UploadFile, File
import csv
import io
from app.models.discipline import Discipline

@router.post("/bulk-upload")
async def bulk_upload_users(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Bulk upload users from CSV.
    CSV Format: id, name, email, password, gender, address, phone_number, discipline_code, roles
    Roles should be semicolon separated.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")

    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    # Validate headers
    required_fields = {'id', 'name', 'email', 'password', 'gender', 'address', 'phone_number', 'roles'}
    if not csv_reader.fieldnames or not required_fields.issubset(set(csv_reader.fieldnames)):
         missing = required_fields - set(csv_reader.fieldnames or [])
         raise HTTPException(status_code=400, detail=f"Missing required columns: {', '.join(missing)}")

    users_created = 0
    errors = []
    
    from app.models.user import UserRoleEntry
    
    for row_idx, row in enumerate(csv_reader):
        try:
            user_id = row.get('id', '').strip() if row.get('id', '') else None
            if not user_id:
                errors.append(f"Row {row_idx}: Missing user id")
                continue
                
            # Check if user exists
            existing_user = db.query(User).filter(User.id == user_id).first()
            if existing_user:
                errors.append(f"Row {row_idx}: User {user_id} already exists")
                continue
                
            # Validate discipline if provided
            discipline_code = row.get('discipline_code', '').strip() if row.get('discipline_code', '') else None
            if discipline_code:
                discipline = db.query(Discipline).filter(Discipline.code == discipline_code).first()
                if not discipline:
                    errors.append(f"Row {row_idx}: Discipline {discipline_code} not found")
                    continue
            else:
                discipline_code = None
            
            roles_str = row.get('roles', '').strip() if row.get('roles', '') else None
            if not roles_str:
                errors.append(f"Row {row_idx}: Missing roles")
                continue
            
            # Create user
            user = User(
                id=user_id,
                name=row.get('name', '').strip(),
                email=row.get('email', '').strip(),
                hashed_password=security.get_password_hash(row.get('password', 'password123').strip()),
                gender=row.get('gender', '').strip(),
                address=row.get('address', '').strip(),
                phone_number=row.get('phone_number', '').strip(),
                is_active=True,
                discipline_code=discipline_code,
            )
            db.add(user)
            db.flush()
            print("User created")
            # Add roles
            if roles_str:
                print("Trying inside roles")
                roles = [r.strip() for r in roles_str.split(';') if r.strip()]
                for role_name in roles:
                    try:
                        role_enum = UserRole(role_name)
                        role_entry = UserRoleEntry(user_id=user.id, role=role_enum)
                        db.add(role_entry)
                    except ValueError:
                        errors.append(f"Row {row_idx}: Invalid role {role_name}")
            
            users_created += 1
            
        except Exception as e:
            errors.append(f"Row {row_idx}: {str(e)}")
            
    db.commit()
    
    return {
        "users_created": users_created,
        "errors": errors
    }


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = security.get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
        
    roles_enums = None
    if "roles" in update_data:
        roles_enums = update_data.pop("roles")

    for field, value in update_data.items():
        setattr(user, field, value)
        
    if roles_enums is not None:
        from app.models.user import UserRoleEntry
        # Replace existing roles
        # Note: We can re-assign the list of UserRoleEntry objects
        user.roles = [UserRoleEntry(role=r) for r in roles_enums]
        
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: str,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Deactivate a user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    db.add(user)
    db.commit()
    return {"message": "User deactivated successfully"}
