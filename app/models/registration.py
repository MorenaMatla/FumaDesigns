from app import db
from datetime import datetime
import random
import string

class Registration(db.Model):
    __tablename__ = 'registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False, index=True)
    confirmation_code = db.Column(db.String(10), unique=True, nullable=False)
    status = db.Column(db.String(20), default='pending')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    blockchain_hash = db.Column(db.String(64), nullable=True)
    
    def generate_confirmation_code(self):
        return ''.join(random.choices(string.digits, k=6))
    
    def confirm_registration(self, code):
        if self.confirmation_code == code and self.status == 'pending':
            self.status = 'confirmed'
            self.confirmed_at = datetime.utcnow()
            return True
        return False
    
    def __repr__(self):
        return f'<Registration {self.student.name} - {self.exam.course.name}>'
