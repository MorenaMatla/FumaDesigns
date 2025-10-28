from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models import User, Registration
from datetime import datetime
import json
import io
import csv

bp = Blueprint('gdpr', __name__, url_prefix='/gdpr')

@bp.route('/export-data')
@login_required
def export_data():
    """Export all user data in JSON format (GDPR Article 15 - Right of Access)"""
    
    user_data = {
        'personal_information': {
            'name': current_user.name,
            'email': current_user.email,
            'student_id': current_user.student_id,
            'role': current_user.role,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
        },
        'gdpr_consent': {
            'consent_given': current_user.gdpr_consent,
            'consent_date': current_user.gdpr_consent_date.isoformat() if current_user.gdpr_consent_date else None,
        },
        'exam_registrations': [],
        'messages': {
            'sent': [],
            'received': []
        },
        'export_metadata': {
            'export_date': datetime.utcnow().isoformat(),
            'export_format': 'JSON',
            'gdpr_compliance': 'Article 15 - Right of Access'
        }
    }
    
    for reg in current_user.registrations.all():
        user_data['exam_registrations'].append({
            'course_name': reg.exam.course.name,
            'course_code': reg.exam.course.code,
            'exam_date': reg.exam.exam_date.isoformat(),
            'registration_date': reg.registered_at.isoformat(),
            'status': reg.status,
            'confirmation_code': reg.confirmation_code,
            'blockchain_hash': reg.blockchain_hash
        })
    
    for msg in current_user.sent_messages.all():
        user_data['messages']['sent'].append({
            'to': msg.receiver.name,
            'subject': msg.subject,
            'body': msg.body,
            'date': msg.created_at.isoformat()
        })
    
    for msg in current_user.received_messages.all():
        user_data['messages']['received'].append({
            'from': msg.sender.name,
            'subject': msg.subject,
            'body': msg.body,
            'date': msg.created_at.isoformat(),
            'read': msg.is_read
        })
    
    json_data = json.dumps(user_data, indent=2)
    
    buffer = io.BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)
    
    filename = f'user_data_{current_user.student_id}_{datetime.utcnow().strftime("%Y%m%d")}.json'
    
    flash('Your data has been exported successfully.', 'success')
    
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name=filename
    )

@bp.route('/request-deletion', methods=['POST'])
@login_required
def request_deletion():
    """Request account deletion (GDPR Article 17 - Right to Erasure)"""
    
    if current_user.role == 'ADMIN':
        flash('Admin accounts cannot be deleted through self-service. Contact system administrator.', 'warning')
        return redirect(url_for('dashboard.settings'))
    
    if hasattr(current_user, 'deletion_requested') and current_user.deletion_requested:
        flash('Your deletion request is already pending review.', 'info')
        return redirect(url_for('dashboard.settings'))
    
    current_user.is_active = False
    current_user.deletion_requested = True
    current_user.deletion_requested_date = datetime.utcnow()
    db.session.commit()
    
    flash('Your account deletion request has been submitted. An administrator will review it shortly. You have been logged out.', 'info')
    
    from flask_login import logout_user
    logout_user()
    
    return redirect(url_for('auth.login'))

@bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information (GDPR Article 16 - Right to Rectification)"""
    from flask import request
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    
    if not name or not email:
        flash('Name and email are required.', 'danger')
        return redirect(url_for('dashboard.settings'))
    
    if email != current_user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already in use by another account.', 'danger')
            return redirect(url_for('dashboard.settings'))
    
    current_user.name = name
    current_user.email = email
    db.session.commit()
    
    flash('Your profile has been updated successfully.', 'success')
    return redirect(url_for('dashboard.settings'))

@bp.route('/withdraw-consent', methods=['POST'])
@login_required
def withdraw_consent():
    """Withdraw GDPR consent (GDPR Article 7 - Conditions for consent)"""
    
    current_user.gdpr_consent = False
    current_user.is_active = False
    db.session.commit()
    
    flash('Your consent has been withdrawn. Your account has been deactivated. Contact support to reactivate.', 'warning')
    
    from flask_login import logout_user
    logout_user()
    
    return redirect(url_for('auth.login'))
