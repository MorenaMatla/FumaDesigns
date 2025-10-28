from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Registration, Message

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    unread_messages = current_user.get_unread_messages_count()
    
    recent_registrations = Registration.query.filter_by(
        student_id=current_user.id,
        status='confirmed'
    ).order_by(Registration.registered_at.desc()).limit(5).all()
    
    greeting = get_greeting()
    
    return render_template('dashboard/index.html',
                         greeting=greeting,
                         unread_messages=unread_messages,
                         recent_registrations=recent_registrations)

@bp.route('/messages')
@login_required
def messages():
    unread_messages = current_user.get_unread_messages_count()
    messages_list = current_user.received_messages.order_by(Message.created_at.desc()).all()
    
    return render_template('dashboard/messages.html',
                         unread_messages=unread_messages,
                         messages=messages_list)

@bp.route('/settings')
@login_required
def settings():
    unread_messages = current_user.get_unread_messages_count()
    return render_template('dashboard/settings.html', unread_messages=unread_messages)

@bp.route('/support')
@login_required
def support():
    unread_messages = current_user.get_unread_messages_count()
    return render_template('dashboard/support.html', unread_messages=unread_messages)

@bp.route('/calendar')
@login_required
def calendar():
    unread_messages = current_user.get_unread_messages_count()
    registrations = Registration.query.filter_by(
        student_id=current_user.id,
        status='confirmed'
    ).all()
    
    return render_template('dashboard/calendar.html',
                         unread_messages=unread_messages,
                         registrations=registrations)

def get_greeting():
    from datetime import datetime
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    else:
        return "Good Evening"
