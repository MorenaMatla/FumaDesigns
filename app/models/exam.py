from app import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    courses = db.relationship('Course', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    credits = db.Column(db.Integer, default=3)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    exams = db.relationship('Exam', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'

class Exam(db.Model):
    __tablename__ = 'exams'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    exam_time = db.Column(db.Time, nullable=True)
    duration_minutes = db.Column(db.Integer, default=180)
    venue = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(20), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    max_students = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    registrations = db.relationship('Registration', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_registered_count(self):
        return self.registrations.filter_by(status='confirmed').count()
    
    def is_full(self):
        return self.get_registered_count() >= self.max_students
    
    def __repr__(self):
        return f'<Exam {self.course.name} on {self.exam_date}>'
