from flask import Blueprint, render_template, flash, request, flash, redirect, url_for
from .models import User
from .models import db  # Import the db object
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/home')
def home():
    return "home"

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to dashboard or home if already logged in
        if current_user.is_teacher():
            return redirect(url_for('views.teacher_dashboard'))
        if current_user.is_student():
            return redirect(url_for('views.student_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            from .models import Role as UserRole
            #print(user.role.value)
            #print(role)
            if user.role.value == role.lower():

                flash('Login successful!', category='success')
                login_user(user, remember=True)
                print(f"[DEBUG] auth.py: login successful")
                return redirect(url_for('views.teacher_dashboard'))
            else:
                flash('Invalid role.', category='error')

        else:
            flash('Login failed. Check your email and password.', category='error')
            return render_template("auth/login.html")

    return render_template("auth/login.html")


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # This logs out the user
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

