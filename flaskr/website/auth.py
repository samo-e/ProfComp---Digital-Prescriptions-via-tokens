from flask import Blueprint, render_template, redirect, url_for, request, flash, render_template_string, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User
from datetime import datetime
from .auth_forms import LoginForm, ForgotPasswordForm
import smtplib
from email.message import EmailMessage

auth = Blueprint("auth", __name__)


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

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data

        # Validate input
        if not email or not password:
            flash("Please fill in all fields", "error")
            return render_template("auth/login.html", form=form)

        # Find user
        user = User.query.filter_by(email=email).first()

        # Check credentials and role
        if not user:
            flash("Invalid email or password", "error")
            return render_template("auth/login.html", form=form)

        if not user.check_password(password):
            flash("Invalid email or password", "error")
            return render_template("auth/login.html", form=form)

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
            return render_template("auth/login.html", form=form)

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

    return render_template("auth/login.html", form=form)


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




# Example HTML email template
reset_password_email_html_content = """
<p>Hello,</p>
<p>You requested a password reset. Click the link below to reset your password:</p>
<p><a href="{{ reset_password_url }}">Reset Password</a></p>
<p>If you did not request this, please ignore this email.</p>
"""

def send_reset_password_email(user):
    # Generate full URL for password reset
    reset_password_url = url_for(
        "auth.reset_password",
        token=user.generate_reset_password_token(),
        user_id=user.id,
        _external=True,
    )

    # Render the HTML email body
    email_body = render_template_string(
        reset_password_email_html_content,
        reset_password_url=reset_password_url
    )

    # Create the email
    message = EmailMessage()
    message["Subject"] = "Reset Your Password"
    message["From"] = current_app.config.get("MAIL_DEFAULT_SENDER", "no-reply@example.com")
    message["To"] = user.email
    message.set_content(email_body, subtype="html")

    # Send the email using SMTP
    with smtplib.SMTP(current_app.config.get("MAIL_SERVER", "localhost"), 
                      current_app.config.get("MAIL_PORT", 25)) as server:
        if current_app.config.get("MAIL_USE_TLS", False):
            server.starttls()
        if current_app.config.get("MAIL_USERNAME") and current_app.config.get("MAIL_PASSWORD"):
            server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
        server.send_message(message)



@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return render_template("auth/already_logged_in.html", user=current_user)

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            try:
                send_reset_password_email(user)
            except:
                pass

        flash(
            "Instructions to reset your password were sent to your email address,"
            " if it exists in our system."
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/reset_password_request.html", title="Reset Password", form=form
    )

@auth.route("/reset_password/<token>/<int:user_id>", methods=["GET", "POST"])
def reset_password(token, user_id):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    user = User.validate_reset_password_token(token, user_id)
    if not user:
        return render_template(
            "auth/reset_password_error.html", title="Reset Password error"
        )

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()

        return render_template(
            "auth/reset_password_success.html", title="Reset Password success"
        )

    return render_template(
        "auth/reset_password.html", title="Reset Password", form=form
    )
