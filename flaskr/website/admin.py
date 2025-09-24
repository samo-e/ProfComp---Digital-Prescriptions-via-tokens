from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserRole
from datetime import datetime


admin = Blueprint('admin', __name__)


@admin.route('/admin')
def admin_dashboard():
	# Query teachers and students from the database
	teachers = User.query.filter_by(role=UserRole.TEACHER.value).all()
	students = User.query.filter_by(role=UserRole.STUDENT.value).all()
	return render_template('auth/admin.html', teachers=teachers, students=students)
