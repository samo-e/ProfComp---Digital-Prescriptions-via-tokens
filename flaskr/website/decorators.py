from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_teacher():
            flash('Access denied. Teacher privileges required.', 'error')
            return redirect(url_for('views.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if not current_user.is_student():
            flash('Access denied. Student privileges required.', 'error')
            return redirect(url_for('views.dashboard'))
        return f(*args, **kwargs)
    return decorated_function