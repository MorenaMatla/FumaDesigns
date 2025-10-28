from app import db
from app.models import User, Department, Course, Exam
from app.utils.blockchain import BlockchainManager
from datetime import datetime, date, time, timedelta
import random

def seed_initial_data():
    """Seed initial data for the application"""
    
    if User.query.first() is not None:
        return
    
    BlockchainManager.initialize_blockchain()
    
    admin_user = User(
        name='System Administrator',
        email='admin@university.edu',
        student_id='ADMIN001',
        role='ADMIN',
        gdpr_consent=True,
        gdpr_consent_date=datetime.utcnow()
    )
    admin_user.set_password('admin123')
    db.session.add(admin_user)
    
    faculty_user = User(
        name='Dr. Jane Smith',
        email='faculty@university.edu',
        student_id='FAC001',
        role='FACULTY',
        gdpr_consent=True,
        gdpr_consent_date=datetime.utcnow()
    )
    faculty_user.set_password('faculty123')
    db.session.add(faculty_user)
    
    student_user = User(
        name='Fuma Mpho',
        email='student@university.edu',
        student_id='STU001',
        role='STUDENT',
        gdpr_consent=True,
        gdpr_consent_date=datetime.utcnow()
    )
    student_user.set_password('student123')
    db.session.add(student_user)
    
    ict_dept = Department(
        name='Information & Communication Technology',
        code='ICT'
    )
    db.session.add(ict_dept)
    
    eng_dept = Department(
        name='Engineering',
        code='ENG'
    )
    db.session.add(eng_dept)
    
    bus_dept = Department(
        name='Business Administration',
        code='BUS'
    )
    db.session.add(bus_dept)
    
    db.session.commit()
    
    courses_data = [
        {'name': 'Cloud Computing', 'code': 'ICT301', 'dept': ict_dept, 'desc': 'Introduction to cloud computing technologies and platforms'},
        {'name': 'Cryptography & Network Security', 'code': 'ICT302', 'dept': ict_dept, 'desc': 'Network security and cryptographic protocols'},
        {'name': 'Discrete Mathematics', 'code': 'ICT101', 'dept': ict_dept, 'desc': 'Sets, Proofs & Functions'},
        {'name': 'Programming Fundamentals', 'code': 'ICT102', 'dept': ict_dept, 'desc': 'Loops, Arrays & Functions'},
        {'name': 'Database Systems', 'code': 'ICT201', 'dept': ict_dept, 'desc': 'SQL, NoSQL, and database design'},
        {'name': 'Web Development', 'code': 'ICT202', 'dept': ict_dept, 'desc': 'HTML, CSS, JavaScript, and frameworks'},
        {'name': 'Mobile App Development', 'code': 'ICT303', 'dept': ict_dept, 'desc': 'iOS and Android development'},
        {'name': 'Data Structures & Algorithms', 'code': 'ICT203', 'dept': ict_dept, 'desc': 'Core algorithms and data structures'},
    ]
    
    for course_data in courses_data:
        course = Course(
            name=course_data['name'],
            code=course_data['code'],
            description=course_data['desc'],
            department_id=course_data['dept'].id,
            credits=3
        )
        db.session.add(course)
    
    db.session.commit()
    
    courses = Course.query.all()
    base_date = date.today() + timedelta(days=30)
    
    for i, course in enumerate(courses[:6]):
        exam_date = base_date + timedelta(days=i*3)
        exam = Exam(
            course_id=course.id,
            exam_date=exam_date,
            exam_time=time(9, 0),
            duration_minutes=180,
            venue=f'Hall {chr(65+i)}',
            academic_year='2024/2025',
            semester='Semester 1',
            max_students=100,
            is_active=True
        )
        db.session.add(exam)
    
    db.session.commit()
