from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserRole
from datetime import datetime


admin = Blueprint('admin', __name__)

# Simple form for CSRF protection
class AssignStudentForm(FlaskForm):
	pass

# Password change form
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired('Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])

# Account creation form
class CreateAccountForm(FlaskForm):
    studentnumber = IntegerField('Student Number', validators=[
        DataRequired('Student number is required'),
        NumberRange(min=10000000, max=99999999, message='Student number must be 8 digits')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired('First name is required'),
        Length(min=1, max=50, message='First name must be 1-50 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired('Last name is required'),
        Length(min=1, max=50, message='Last name must be 1-50 characters')
    ])
    email = StringField('Email', validators=[
        Optional(),
        Email('Invalid email address'),
        Length(max=100, message='Email must be less than 100 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required'),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    role = SelectField('Role', choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin')
    ], validators=[DataRequired('Role is required')])

@admin.route('/admin')
def admin_dashboard():
	teachers = User.query.filter_by(role=UserRole.TEACHER.value).all()
	students = User.query.filter_by(role=UserRole.STUDENT.value).all()
	admins = User.query.filter_by(role=UserRole.ADMIN.value).all()
	return render_template('admin/admin.html', teachers=teachers, students=students, admins=admins)

# User profile page (blank for now)
@admin.route('/admin/user/<int:user_id>', methods=['GET', 'POST'])
def teacher_profile(user_id):
	user = User.query.get_or_404(user_id)
	students = []
	form = AssignStudentForm()
	password_form = ChangePasswordForm()
	if user.is_teacher():
		students = User.query.filter_by(role=UserRole.STUDENT.value).all()
	return render_template('admin/teacher_profile.html', user=user, students=students, form=form, password_form=password_form)

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
	return redirect(url_for('admin.teacher_profile', user_id=teacher_id))

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
	return redirect(url_for('admin.teacher_profile', user_id=teacher_id))

# Route to change user password
@admin.route('/admin/change_password/<int:user_id>', methods=['POST'])
def change_password(user_id):
	user = User.query.get_or_404(user_id)
	password_form = ChangePasswordForm()
	
	if password_form.validate_on_submit():
		user.set_password(password_form.new_password.data)
		db.session.commit()
		flash(f'Password updated successfully for {user.get_full_name()}!', 'success')
	else:
		flash('Password change failed. Please check the requirements.', 'error')
	
	# Redirect back to appropriate profile
	if user.is_teacher():
		return redirect(url_for('admin.teacher_profile', user_id=user_id))
	else:
		return redirect(url_for('admin.student_profile', user_id=user_id))

# Student profile route
@admin.route('/admin/student/<int:user_id>')
def student_profile(user_id):
	user = User.query.get_or_404(user_id)
	password_form = ChangePasswordForm()
	return render_template('admin/student_profile.html', user=user, password_form=password_form)


# Account creation route
@admin.route('/admin/create_account', methods=['GET', 'POST'])
def create_account():
    
    form = CreateAccountForm()
    
    if form.validate_on_submit():
        # Check for duplicate student number
        if form.studentnumber.data:
            existing_student_num = User.query.filter_by(studentnumber=form.studentnumber.data).first()
            if existing_student_num:
                flash(f'Student number {form.studentnumber.data} already exists.', 'error')
                return render_template('admin/account_create.html', form=form)
        
        # Check for duplicate email if provided
        if form.email.data:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash(f'Email {form.email.data} already exists.', 'error')
                return render_template('admin/account_create.html', form=form)
        
        # Generate email if not provided
        email = form.email.data
        if not email:
            # Create email from first name, last name, and student number
            email = f"{form.first_name.data.lower()}.{form.last_name.data.lower()}.{form.studentnumber.data}@student.edu"
            
            # Check if generated email already exists
            counter = 1
            original_email = email
            while User.query.filter_by(email=email).first():
                email = f"{original_email.split('@')[0]}.{counter}@student.edu"
                counter += 1
        
        try:
            # Create new user
            new_user = User(
                studentnumber=form.studentnumber.data,
                email=email,
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                created_at=datetime.now(),
                is_active=True
            )
            new_user.set_password(form.password.data)
            
            db.session.add(new_user)
            db.session.commit()
            
            # Store success info in session to prevent browser back issues
            flash(f'Account created successfully for {new_user.get_full_name()} ({email})', 'success')
            # Clear the form by redirecting to success page
            return redirect(url_for('admin.account_creation_success', user_id=new_user.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return render_template('admin/account_create.html', form=form)
    
    return render_template('admin/account_create.html', form=form)

# Account creation success page to prevent browser back issues
@admin.route('/admin/account_creation_success/<int:user_id>')
def account_creation_success(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/account_success.html', user=user)

