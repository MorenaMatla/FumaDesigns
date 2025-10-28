from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db, limiter
from app.models import User
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        student_id = request.form.get('student_id', '').strip().upper()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        gdpr_consent = request.form.get('gdpr_consent') == 'on'
        
        if not all([name, email, student_id, password, password_confirm]):
            flash('All fields are required.', 'danger')
            return render_template('auth/signup.html')
        
        if password != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/signup.html')
        
        if not gdpr_consent:
            flash('You must accept the privacy policy and terms.', 'warning')
            return render_template('auth/signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/signup.html')
        
        if User.query.filter_by(student_id=student_id).first():
            flash('Student ID already registered.', 'danger')
            return render_template('auth/signup.html')
        
        user = User(
            name=name,
            email=email,
            student_id=student_id,
            role='STUDENT',
            gdpr_consent=gdpr_consent,
            gdpr_consent_date=datetime.utcnow() if gdpr_consent else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/signup.html')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account has been deactivated. Please contact support.', 'danger')
            return render_template('auth/login.html')
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        flash(f'Welcome back, {user.name}!', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
