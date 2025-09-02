from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, SignUpForm
from .models import get_user_by_email, create_user, verify_user_credentials

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        password = form.password.data
        
        # Use the verify_user_credentials helper function
        user = verify_user_credentials(email, password)
        
        if user:
            login_user(user, remember=True)  # Add remember me functionality
            flash(f'Welcome back, {user.name}!', 'success')
            
            # Redirect based on user role
            next_page = request.args.get('next')  # Handle redirect after login
            if next_page:
                return redirect(next_page)
            elif user.is_teacher():
                return redirect(url_for('views.teacher_dashboard'))
            else:
                return redirect(url_for('views.student_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
            # Log failed attempt for security monitoring (in production)
            print(f"Failed login attempt for email: {email}")
    
    return render_template('auth/login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()  # Normalize email
        name = form.name.data.strip()
        password = form.password.data
        role = form.role.data
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            flash('An account with this email already exists. Please use a different email or sign in.', 'error')
        else:
            # Create new user with hashed password
            try:
                user = create_user(
                    email=email,
                    password=password,  # Will be hashed in create_user
                    role=role,
                    name=name
                )
                
                # Log the user in automatically after signup
                login_user(user, remember=True)
                flash(f'Account created successfully! Welcome, {user.name}!', 'success')
                
                # Send welcome email (in production)
                # send_welcome_email(user.email, user.name)
                
                # Redirect based on role
                if user.is_teacher():
                    flash('You can now create and manage scenarios for your students.', 'info')
                    return redirect(url_for('views.teacher_dashboard'))
                else:
                    flash('You can now access learning scenarios assigned by your teacher.', 'info')
                    return redirect(url_for('views.student_dashboard'))
                    
            except Exception as e:
                flash('An error occurred while creating your account. Please try again.', 'error')
                print(f"Error creating user: {str(e)}")  # Log for debugging
    
    return render_template('auth/signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    user_name = current_user.name
    logout_user()
    flash(f'You have been logged out successfully. Goodbye, {user_name}!', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/check-email', methods=['POST'])
def check_email():
    """AJAX endpoint to check if email is already registered"""
    email = request.get_json().get('email', '').strip().lower()
    if email and get_user_by_email(email):
        return {'exists': True}, 200
    return {'exists': False}, 200

# Optional: Add password reset functionality
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests"""
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    
    # Implement password reset logic here
    # This would typically involve:
    # 1. Sending a reset token via email
    # 2. Validating the token
    # 3. Allowing user to set new password
    
    flash('Password reset functionality coming soon!', 'info')
    return redirect(url_for('auth.login'))