from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Exam, Registration, Course, Department
from app.utils.blockchain import BlockchainManager
from datetime import datetime
import json

bp = Blueprint('exams', __name__, url_prefix='/exams')

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        department_id = request.form.get('department_id')
        course_ids = request.form.getlist('course_ids')
        exam_date = request.form.get('exam_date')
        academic_year = request.form.get('academic_year', '2024/2025')
        
        if not all([department_id, course_ids, exam_date]):
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('exams.register'))
        
        registered_exams = []
        
        for course_id in course_ids:
            exam = Exam.query.filter_by(
                course_id=course_id,
                academic_year=academic_year,
                is_active=True
            ).first()
            
            if not exam:
                flash(f'No active exam found for selected course.', 'warning')
                continue
            
            existing = Registration.query.filter_by(
                student_id=current_user.id,
                exam_id=exam.id
            ).first()
            
            if existing:
                flash(f'You are already registered for {exam.course.name}.', 'warning')
                continue
            
            if exam.is_full():
                flash(f'Exam for {exam.course.name} is full.', 'warning')
                continue
            
            registration = Registration(
                student_id=current_user.id,
                exam_id=exam.id,
                status='pending'
            )
            registration.confirmation_code = registration.generate_confirmation_code()
            
            db.session.add(registration)
            db.session.flush()
            
            blockchain_data = {
                'registration_id': registration.id,
                'student_id': current_user.student_id,
                'student_name': current_user.name,
                'course_code': exam.course.code,
                'course_name': exam.course.name,
                'exam_date': str(exam.exam_date),
                'confirmation_code': registration.confirmation_code,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            block = BlockchainManager.add_block(blockchain_data, record_type='registration')
            registration.blockchain_hash = block.current_hash
            
            registered_exams.append(registration)
        
        db.session.commit()
        
        if registered_exams:
            flash(f'Successfully registered for {len(registered_exams)} exam(s). Check your confirmation codes.', 'success')
            return redirect(url_for('exams.confirm'))
        else:
            flash('No exams were registered.', 'warning')
            return redirect(url_for('exams.register'))
    
    departments = Department.query.all()
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('exams/register.html',
                         departments=departments,
                         unread_messages=unread_messages)

@bp.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    if request.method == 'POST':
        registration_id = request.form.get('registration_id')
        code = request.form.get('confirmation_code', '').strip()
        
        registration = Registration.query.get(registration_id)
        
        if not registration or registration.student_id != current_user.id:
            flash('Invalid registration.', 'danger')
            return redirect(url_for('exams.confirm'))
        
        if registration.confirm_registration(code):
            db.session.commit()
            flash(f'Exam registration confirmed for {registration.exam.course.name}!', 'success')
            return redirect(url_for('exams.view_registered'))
        else:
            flash('Invalid confirmation code or registration already confirmed.', 'danger')
    
    pending_registrations = Registration.query.filter_by(
        student_id=current_user.id,
        status='pending'
    ).all()
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('exams/confirm.html',
                         registrations=pending_registrations,
                         unread_messages=unread_messages)

@bp.route('/registered')
@login_required
def view_registered():
    confirmed_registrations = Registration.query.filter_by(
        student_id=current_user.id,
        status='confirmed'
    ).order_by(Registration.confirmed_at.desc()).all()
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('exams/registered.html',
                         registrations=confirmed_registrations,
                         unread_messages=unread_messages)

@bp.route('/api/courses/<int:department_id>')
@login_required
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'code': c.code,
        'credits': c.credits
    } for c in courses])
