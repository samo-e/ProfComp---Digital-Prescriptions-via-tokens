from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, SignUpForm
from .models import get_user_by_email, create_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            
            if user.is_teacher():
                return redirect(url_for('views.teacher_dashboard'))
            else:
                return redirect(url_for('views.student_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        existing_user = get_user_by_email(form.email.data)
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
        else:
            user = create_user(
                email=form.email.data,
                password=form.password.data,
                role=form.role.data,
                name=form.name.data
            )
            login_user(user)
            flash(f'Account created successfully! Welcome, {user.name}!', 'success')
            
            if user.is_teacher():
                return redirect(url_for('views.teacher_dashboard'))
            else:
                return redirect(url_for('views.student_dashboard'))
    
    return render_template('auth/signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))