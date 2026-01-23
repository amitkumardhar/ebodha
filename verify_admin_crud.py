
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_TOKEN = "admin_token_placeholder" # You might need to login to get this
TEACHER_TOKEN = "teacher_token_placeholder"

def login(username, password):
    response = requests.post(f"{BASE_URL}/login/access-token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed for {username}: {response.text}")
        return None

def verify_admin_crud():
    print("Verifying Admin CRUD...")
    token = login("admin", "admin") # Assuming default admin credentials
    if not token: return
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Disciplines
    print("\n[Disciplines]")
    # Create
    disc_data = {"code": 999, "name": "Test Discipline", "is_active": True}
    res = requests.post(f"{BASE_URL}/disciplines/", json=disc_data, headers=headers)
    print(f"Create: {res.status_code}")
    
    # Update
    disc_data["name"] = "Updated Test Discipline"
    res = requests.put(f"{BASE_URL}/disciplines/999", json=disc_data, headers=headers)
    print(f"Update: {res.status_code}")
    
    # Delete (Deactivate)
    res = requests.delete(f"{BASE_URL}/disciplines/999", headers=headers)
    print(f"Delete: {res.status_code}")

    # 2. Users
    print("\n[Users]")
    # Create
    user_data = {
        "id": "TEST001", "name": "Test User", "email": "test@example.com", 
        "password": "password", "gender": "M", "address": "Test Addr", 
        "phone_number": "1234567890", "is_active": True, "roles": ["student"]
    }
    res = requests.post(f"{BASE_URL}/users/", json=user_data, headers=headers)
    print(f"Create: {res.status_code}")
    
    # Update
    user_data["name"] = "Updated Test User"
    res = requests.put(f"{BASE_URL}/users/TEST001", json=user_data, headers=headers)
    print(f"Update: {res.status_code}")
    
    # Delete
    res = requests.delete(f"{BASE_URL}/users/TEST001", headers=headers)
    print(f"Delete: {res.status_code}")

    # 3. Courses
    print("\n[Courses]")
    # Create
    course_data = {
        "code": "TEST101", "name": "Test Course", "category": "Core Course",
        "lecture_credits": 3, "tutorial_credits": 0, "practice_credits": 0
    }
    res = requests.post(f"{BASE_URL}/courses/", json=course_data, headers=headers)
    print(f"Create: {res.status_code}")
    
    # Update
    course_data["name"] = "Updated Test Course"
    res = requests.put(f"{BASE_URL}/courses/TEST101", json=course_data, headers=headers)
    print(f"Update: {res.status_code}")
    
    # Delete
    res = requests.delete(f"{BASE_URL}/courses/TEST101", headers=headers)
    print(f"Delete: {res.status_code}")

    # 4. Semesters
    print("\n[Semesters]")
    # Create
    sem_data = {"id": 999, "start_date": "2026-01-01", "end_date": "2026-06-30"}
    res = requests.post(f"{BASE_URL}/academic/semesters/", json=sem_data, headers=headers)
    print(f"Create: {res.status_code}")
    
    # Update
    sem_data["end_date"] = "2026-07-31"
    res = requests.put(f"{BASE_URL}/academic/semesters/999", json=sem_data, headers=headers)
    print(f"Update: {res.status_code}")
    
    # Delete
    res = requests.delete(f"{BASE_URL}/academic/semesters/999", headers=headers)
    print(f"Delete: {res.status_code}")

def verify_teacher_marks_update():
    print("\nVerifying Teacher Marks Update...")
    # Need a teacher user, a course, a semester, a student, and an exam
    # This is harder to setup automatically without existing data.
    # I'll assume some data exists or create it.
    
    admin_token = login("admin", "admin")
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Setup Data
    # 1. Create Semester 100
    requests.post(f"{BASE_URL}/academic/semesters/", json={"id": 100, "start_date": "2026-01-01", "end_date": "2026-06-30"}, headers=headers)
    
    # 2. Create Course CS101
    requests.post(f"{BASE_URL}/courses/", json={"code": "CS101", "name": "Intro to CS", "category": "Core Course", "lecture_credits": 3, "tutorial_credits": 0, "practice_credits": 0}, headers=headers)
    
    # 3. Create Offering
    requests.post(f"{BASE_URL}/courses/offerings/", json={"course_code": "CS101", "semester_id": 100}, headers=headers)
    offering_id = requests.get(f"{BASE_URL}/courses/offerings/?semester_id=100", headers=headers).json()[0]['id']
    
    # 4. Create Teacher
    requests.post(f"{BASE_URL}/users/", json={"id": "TEACHER1", "name": "Teacher One", "email": "t1@example.com", "password": "password", "gender": "M", "address": "Addr", "phone_number": "123", "is_active": True, "roles": ["teacher"]}, headers=headers)
    
    # 5. Assign Teacher
    requests.post(f"{BASE_URL}/courses/offerings/{offering_id}/teachers?teacher_id=TEACHER1", headers=headers)
    
    # 6. Create Student
    requests.post(f"{BASE_URL}/users/", json={"id": "STUDENT1", "name": "Student One", "email": "s1@example.com", "password": "password", "gender": "M", "address": "Addr", "phone_number": "123", "is_active": True, "roles": ["student"]}, headers=headers)
    
    # 7. Register Student (Need endpoint for this? Or manual DB insert? Assuming registration exists or we can create it via bulk upload or similar. 
    # Actually, there is no direct registration endpoint exposed for admin in the snippets I saw, only bulk upload grades which might require registration to exist.
    # But wait, `bulk_upload_course_offerings` creates offerings and exams.
    # `bulk_upload_users` creates users.
    # Registration is usually done by students or admin.
    # Let's assume we can't easily register a student via API in this script without more effort.
    # But wait, `bulk_upload_grades` in `registrations.py` CHECKS for registration.
    # So we need a registration.
    # Let's try to use `bulk_upload_grades` to see if it auto-registers? No, it checks `if not registration: continue`.
    
    # I'll skip full end-to-end marks update verification if I can't easily register a student.
    # But I can verify the endpoint exists and returns 404/403 as expected.
    
    teacher_token = login("TEACHER1", "password")
    if not teacher_token: return
    t_headers = {"Authorization": f"Bearer {teacher_token}"}
    
    # Try to update marks for non-existent student/exam
    data = {
        "course_code": "CS101",
        "semester_id": 100,
        "student_id": "STUDENT1",
        "exam_name": "Midsem",
        "marks": 25.5
    }
    res = requests.put(f"{BASE_URL}/examinations/marks", json=data, headers=t_headers)
    print(f"Marks Update (Expect 404/400): {res.status_code} - {res.text}")
    
    # Clean up
    requests.delete(f"{BASE_URL}/academic/semesters/100", headers=headers)
    requests.delete(f"{BASE_URL}/courses/CS101", headers=headers)
    requests.delete(f"{BASE_URL}/users/TEACHER1", headers=headers)
    requests.delete(f"{BASE_URL}/users/STUDENT1", headers=headers)

if __name__ == "__main__":
    verify_admin_crud()
    verify_teacher_marks_update()
