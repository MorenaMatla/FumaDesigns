import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    DEPARTMENTS = [
        'Information & Communication Technology',
        'Engineering',
        'Business Administration',
        'Health Sciences',
        'Education',
        'Arts & Humanities'
    ]
    
    COURSES = {
        'Information & Communication Technology': [
            'Cloud Computing',
            'Cryptography & Network Security',
            'Discrete Mathematics',
            'Programming Fundamentals',
            'Database Systems',
            'Web Development',
            'Mobile App Development',
            'Data Structures & Algorithms'
        ],
        'Engineering': [
            'Engineering Mathematics',
            'Physics for Engineers',
            'Circuit Analysis',
            'Thermodynamics'
        ],
        'Business Administration': [
            'Business Strategy',
            'Marketing Management',
            'Financial Accounting',
            'Operations Management'
        ]
    }
    
    ROLES = {
        'STUDENT': {
            'name': 'Student',
            'permissions': ['view_own_data', 'register_exams', 'view_exams', 'view_messages']
        },
        'FACULTY': {
            'name': 'Faculty',
            'permissions': ['view_own_data', 'view_all_students', 'manage_exams', 'view_analytics', 'send_messages']
        },
        'ADMIN': {
            'name': 'Administrator',
            'permissions': ['view_all_data', 'manage_users', 'manage_exams', 'view_analytics', 'manage_security', 'access_blockchain', 'send_messages']
        }
    }
    
    DATA_CLASSIFICATION = {
        'PUBLIC': ['course_names', 'department_names', 'exam_dates'],
        'PRIVATE': ['student_names', 'email_addresses', 'student_ids'],
        'CONFIDENTIAL': ['exam_results', 'registration_records', 'messages'],
        'RESTRICTED': ['passwords', 'security_configs', 'blockchain_keys', 'admin_logs']
    }
