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

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        # Redirect to dashboard or home if already logged in
        return redirect(url_for('views.teacher_dashboard'))  # or student_dashboard, or a general dashboard

    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        # Generate username by combining first and last name with a space
        username = f"{first_name} {last_name}".strip()

        error = False

        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
            error = True

        if len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
            error = True

        if password1 != password2:
            flash('Passwords don\'t match.', category='error')
            error = True

        if len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
            error = True

        if role not in ['teacher', 'student']:
            flash('Please select a valid role.', category='error')
            error = True

        if error:
            return render_template('auth/signup.html')

        # Convert role string to Role enum
        from .models import Role as UserRole
        user_role = UserRole.TEACHER if role == 'teacher' else UserRole.STUDENT

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password1, method='pbkdf2:sha256', salt_length=16),
            role=user_role
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! Please log in.', category='success')
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while creating your account: {str(e)}', category='error')
            return render_template('auth/signup.html')

    # GET request - just show the signup form
    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()  # This logs out the user
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))

