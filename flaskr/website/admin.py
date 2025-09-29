from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_wtf import FlaskForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserRole
from datetime import datetime


admin = Blueprint('admin', __name__)

# Simple form for CSRF protection
class AssignStudentForm(FlaskForm):
	pass

@admin.route('/admin')
def admin_dashboard():
	teachers = User.query.filter_by(role=UserRole.TEACHER.value).all()
	students = User.query.filter_by(role=UserRole.STUDENT.value).all()
	return render_template('auth/admin.html', teachers=teachers, students=students)

# User profile page (blank for now)
@admin.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
	user = User.query.get_or_404(user_id)
	students = []
	form = AssignStudentForm()
	if user.is_teacher():
		students = User.query.filter_by(role=UserRole.STUDENT.value).all()
	return render_template('auth/user_profile.html', user=user, students=students, form=form)

# Route to assign a student to a teacher


@admin.route('/admin/assign_student', methods=['POST'])
def assign_student():
	teacher_id = int(request.form['teacher_id'])
	student_id = int(request.form['student_id'])
	teacher = User.query.get_or_404(teacher_id)
	student = User.query.get_or_404(student_id)
	if student not in teacher.students:
		teacher.students.append(student)
		db.session.commit()
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			# Return student info for live update
			return jsonify(
				success=True,
				message='Student assigned successfully!',
				student={
					'id': student.id,
					'name': student.get_full_name(),
					'email': student.email,
					'teacher_id': teacher.id
				},
				csrf_token=request.form.get('csrf_token')
			)
		flash('Student assigned successfully!', 'success')
	else:
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return jsonify(success=False, message='Student already assigned!')
		flash('Student already assigned!', 'warning')
	return redirect(url_for('admin.user_profile', user_id=teacher_id))

# Route to unassign a student from a teacher
@admin.route('/admin/unassign_student', methods=['POST'])
def unassign_student():
	teacher_id = int(request.form['teacher_id'])
	student_id = int(request.form['student_id'])
	teacher = User.query.get_or_404(teacher_id)
	student = User.query.get_or_404(student_id)
	if student in teacher.students:
		teacher.students.remove(student)
		db.session.commit()
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return jsonify(success=True, message='Student unassigned successfully!')
		flash('Student unassigned successfully!', 'success')
	else:
		if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
			return jsonify(success=False, message='Student was not assigned!')
		flash('Student was not assigned!', 'warning')
	return redirect(url_for('admin.user_profile', user_id=teacher_id))

