from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Registration, Exam, Course, User
from app.utils.decorators import permission_required
import json

bp = Blueprint('ai_analytics', __name__, url_prefix='/analytics')

@bp.route('/')
@login_required
@permission_required('view_analytics')
def index():
    unread_messages = current_user.get_unread_messages_count()
    
    return render_template('ai_analytics/index.html',
                         unread_messages=unread_messages)

@bp.route('/api/registration-trends')
@login_required
@permission_required('view_analytics')
def registration_trends():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    trend_data = db.session.query(
        func.date(Registration.registered_at).label('date'),
        func.count(Registration.id).label('count')
    ).filter(
        Registration.registered_at >= thirty_days_ago
    ).group_by(
        func.date(Registration.registered_at)
    ).all()
    
    return jsonify({
        'labels': [str(item.date) for item in trend_data],
        'data': [item.count for item in trend_data]
    })

@bp.route('/api/popular-courses')
@login_required
@permission_required('view_analytics')
def popular_courses():
    from sqlalchemy import func
    
    popular = db.session.query(
        Course.name,
        func.count(Registration.id).label('registrations')
    ).join(
        Exam, Course.id == Exam.course_id
    ).join(
        Registration, Exam.id == Registration.exam_id
    ).filter(
        Registration.status == 'confirmed'
    ).group_by(
        Course.name
    ).order_by(
        func.count(Registration.id).desc()
    ).limit(10).all()
    
    return jsonify({
        'labels': [item.name for item in popular],
        'data': [item.registrations for item in popular]
    })

@bp.route('/api/predictions')
@login_required
@permission_required('view_analytics')
def predictions():
    try:
        from app.utils.ml_models import get_predictions
        predictions_data = get_predictions()
        return jsonify(predictions_data)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'predictions': []
        })
