from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Exam, Registration, Department, Course, Message
from app.utils.blockchain import BlockchainManager
from app.utils.decorators import role_required, permission_required
from config import Config

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/')
@login_required
@permission_required('view_analytics')
def index():
    total_students = User.query.filter_by(role='STUDENT').count()
    total_exams = Exam.query.filter_by(is_active=True).count()
    total_registrations = Registration.query.filter_by(status='confirmed').count()
    
    is_valid, message = BlockchainManager.verify_chain()
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('admin/index.html',
                         total_students=total_students,
                         total_exams=total_exams,
                         total_registrations=total_registrations,
                         blockchain_valid=is_valid,
                         blockchain_message=message,
                         unread_messages=unread_messages)

@bp.route('/blockchain')
@login_required
@permission_required('access_blockchain')
def blockchain():
    blocks = BlockchainManager.get_all_blocks()
    is_valid, message = BlockchainManager.verify_chain()
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('admin/blockchain.html',
                         blocks=blocks,
                         is_valid=is_valid,
                         message=message,
                         unread_messages=unread_messages)

@bp.route('/security')
@login_required
@permission_required('manage_security')
def security():
    data_classification = Config.DATA_CLASSIFICATION
    roles = Config.ROLES
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('admin/security.html',
                         data_classification=data_classification,
                         roles=roles,
                         unread_messages=unread_messages)

@bp.route('/users')
@login_required
@permission_required('manage_users')
def users():
    all_users = User.query.all()
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('admin/users.html',
                         users=all_users,
                         unread_messages=unread_messages)

@bp.route('/gdpr')
@login_required
@permission_required('view_all_data')
def gdpr():
    users_with_consent = User.query.filter_by(gdpr_consent=True).count()
    users_without_consent = User.query.filter_by(gdpr_consent=False).count()
    
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('admin/gdpr.html',
                         users_with_consent=users_with_consent,
                         users_without_consent=users_without_consent,
                         unread_messages=unread_messages)
