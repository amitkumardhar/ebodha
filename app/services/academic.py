from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.discipline import Discipline
from app.models.examination import Registration, Compartment as CompartmentRegistration
from app.schemas.academic import AcademicHistory, AcademicHistorySemester, AcademicHistoryCourse

def get_student_academic_history(db: Session, student_id: str) -> AcademicHistory:
    """
    Calculate and return the academic history for a student.
    """
    user = db.query(User).filter(User.id == student_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Get all registrations
    registrations = db.query(Registration).filter(Registration.student_id == student_id).all()
    
    # Get all compartment registrations
    compartment_regs = db.query(CompartmentRegistration).filter(CompartmentRegistration.student_id == student_id).all()
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
                "total_credits": 0.0,
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
