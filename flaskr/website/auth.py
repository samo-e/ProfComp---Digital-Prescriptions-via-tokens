from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserRole
from datetime import datetime

auth = Blueprint("auth", __name__)


@auth.context_processor
def inject_globals():
    return current_app.config["GLOBALS"]


@auth.route("/home")
def home():
    """Home page - redirects based on user role"""
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if current_user.is_teacher():
        return redirect(url_for("views.teacher_dashboard"))
    else:
        return redirect(url_for("views.student_dashboard"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login"""
    # Check if user is trying to switch accounts (has 'switch' parameter)
    if request.args.get("switch") == "true" and current_user.is_authenticated:
        logout_user()
        flash("You have been logged out. Please login with your new account.", "info")
        return redirect(url_for("auth.login"))

    # If already logged in and trying to access login page
    if current_user.is_authenticated:
        # Show a page with options
        if request.method == "GET":
            return render_template("auth/already_logged_in.html", user=current_user)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # role = request.form.get("role")  # 'teacher' or 'student'
        remember = request.form.get("remember") == "on"

        # Validate input
        if not email or not password:
            flash("Please fill in all fields", "error")
            return render_template("auth/login.html")

        # Find user
        user = User.query.filter_by(email=email).first()

        # Check credentials and role
        if not user:
            flash("Invalid email or password", "error")
            return render_template("auth/login.html")

        if not user.check_password(password):
            flash("Invalid email or password", "error")
            return render_template("auth/login.html")

        # Check if role matches
        # role_value = "teacher" if role == "Teacher" else "student"
        # if user.role != role_value:
        #     flash(f"This account is not registered as a {role}", "error")
        #     return render_template("auth/login.html")

        # Check if account is active
        if not user.is_active:
            flash(
                "Your account has been deactivated. Please contact an administrator.",
                "error",
            )
            return render_template("auth/login.html")

        # If a different user is trying to login, logout the current user first
        if current_user.is_authenticated and current_user.id != user.id:
            logout_user()

        # Update last login time
        user.last_login = datetime.now()
        db.session.commit()

        # Log the user in
        login_user(user, remember=remember)

        # Flash success message
        flash(f"Welcome back, {user.get_full_name()}!", "success")

        # Redirect based on role
        next_page = request.args.get("next")
        if next_page:
            return redirect(next_page)

        if user.is_teacher():
            return redirect(url_for("views.teacher_dashboard"))
        else:
            return redirect(url_for("views.student_dashboard"))

    return render_template("auth/login.html")


@auth.route("/logout")
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash("You have been logged out successfully", "info")
    return redirect(url_for("auth.login"))


@auth.route("/profile")
@login_required
def profile():
    """User profile page"""
    return render_template("auth/profile.html", user=current_user)


@auth.route("/change-password", methods=["POST"])
@login_required
def change_password():
    """Handle password change"""
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    # Validate current password
    if not current_user.check_password(current_password):
        flash("Current password is incorrect", "error")
        return redirect(url_for("auth.profile"))

    # Validate new password
    if len(new_password) < 8:
        flash("New password must be at least 8 characters long", "error")
        return redirect(url_for("auth.profile"))

    if new_password != confirm_password:
        flash("New passwords do not match", "error")
        return redirect(url_for("auth.profile"))

    # Update password
    current_user.set_password(new_password)
    db.session.commit()

    flash("Password changed successfully", "success")
    return redirect(url_for("auth.profile"))


# Admin routes (for teachers to manage student accounts)
@auth.route("/admin/users")
@login_required
def admin_users():
    """Admin page to manage users (teachers only)"""
    if not current_user.is_teacher():
        flash("You do not have permission to access this page", "error")
        return redirect(url_for("auth.home"))

    users = User.query.all()
    return render_template("auth/admin_users.html", users=users)


@auth.route("/admin/toggle-user-status/<int:user_id>", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status (teachers only)"""
    if not current_user.is_teacher():
        flash("You do not have permission to perform this action", "error")
        return redirect(url_for("auth.home"))

    user = User.query.get_or_404(user_id)

    # Prevent deactivating yourself
    if user.id == current_user.id:
        flash("You cannot deactivate your own account", "error")
        return redirect(url_for("auth.admin_users"))

    user.is_active = not user.is_active
    db.session.commit()

    status = "activated" if user.is_active else "deactivated"
    flash(f"User {user.email} has been {status}", "success")

    return redirect(url_for("auth.admin_users"))
