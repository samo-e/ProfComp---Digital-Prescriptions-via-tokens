import random
import string
import os
import re
from flask import send_from_directory, send_file, abort

import csv
import io
import pandas as pd
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    jsonify,
    make_response,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Optional, Length, NumberRange
from flask_login import login_required, current_user
from .models import (
    db,
    User,
    UserRole,
    ScenarioPatient,
    StudentScenario,
    Prescription,
    Patient,
    Scenario,
)
from datetime import datetime
from functools import wraps

admin = Blueprint("admin", __name__)

_last_created_csv_path = None


@admin.route("/admin/update_user/<int:user_id>", methods=["POST"])
@login_required
def update_user(user_id):
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip()
    studentnumber = request.form.get("studentnumber", "").strip()

    # Only update if a value is provided
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if studentnumber:
        user.studentnumber = studentnumber
    if email and email != user.email:
        # Check for email uniqueness
        if User.query.filter(User.email == email, User.id != user.id).first():
            flash("Email already exists for another user.", "danger")
            return redirect(url_for("admin.teacher_profile", user_id=user.id))
        user.email = email

    db.session.commit()
    # flash("User information updated successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))


# Route to list all CSV exports
@admin.route("/admin/csv_exports")
@login_required
def csv_exports():
    if current_user.role != "admin":
        # flash("Admin privileges required.", "error")
        return redirect(url_for("views.home"))
    export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    try:
        files = [f for f in os.listdir(export_dir) if f.endswith(".zip")]
        files.sort(reverse=True)
    except Exception:
        files = []
    return render_template("admin/admin_csv.html", csv_files=files)


# Route to download a specific CSV export
@admin.route("/admin/download_csv/<filename>")
@login_required
def download_csv(filename):
    if current_user.role != "admin":
        # flash("Admin privileges required.", "error")
        return redirect(url_for("views.home"))
    export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    # Only allow ZIP files to be downloaded
    if not filename.endswith(".zip"):
        # flash("Only encrypted ZIP files are available for download.", "error")
        return redirect(url_for("admin.csv_exports"))
    return send_from_directory(export_dir, filename, as_attachment=True)


# Function to export and encrypt CSV as password-protected ZIP
import pyzipper


def export_and_encrypt_csv(csv_filename, zip_filename, password):
    """
    Encrypts a CSV file as a password-protected ZIP file using pyzipper.
    Args:
        csv_filename (str): Path to the CSV file to encrypt.
        zip_filename (str): Path to the output ZIP file.
        password (str): Password for ZIP encryption.
    """
    if not os.path.exists(csv_filename):
        raise FileNotFoundError(f"CSV file '{csv_filename}' does not exist.")
    with pyzipper.AESZipFile(
        zip_filename, "w", compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES
    ) as zf:
        zf.setpassword(password.encode())
        zf.write(csv_filename, arcname=os.path.basename(csv_filename))
    # Delete the original CSV after encryption
    try:
        os.remove(csv_filename)
        # print(f"Original CSV deleted: {csv_filename}")
    except Exception as e:
        pass
        # print(f"Failed to delete CSV: {e}")
    # print(f"Encrypted ZIP created: {zip_filename}")


@admin.route("/admin/download_last_created_accounts_csv")
@login_required
def download_last_created_accounts_csv():
    global _last_created_csv_path
    if current_user.role != "admin":
        return "Access denied", 403
    if not _last_created_csv_path or not os.path.exists(_last_created_csv_path):
        return "No CSV available", 404
    return send_file(_last_created_csv_path, as_attachment=True)


# Exempt the batch_create_accounts route from CSRF protection using the csrf instance
@admin.route("/admin/export_accounts_zip")
@login_required
def export_accounts_zip():
    if current_user.role != "admin":
        # flash("Admin privileges required.", "error")
        return redirect(url_for("views.home"))
    # Example: Query all users and export to CSV
    users = User.query.all()
    export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
    os.makedirs(export_dir, exist_ok=True)
    csv_filename = os.path.join(export_dir, "accounts_export.csv")
    zip_filename = os.path.join(export_dir, "accounts_export.zip")
    password = "ChangeThisPassword"  # Set a secure password here
    # Write users to CSV
    # WARNING: This assumes you have stored the plaintext password somewhere accessible.
    # If you do not have plaintext passwords, you must generate and store them at account creation.
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "id",
                "studentnumber",
                "email",
                "password",
                "role",
                "first_name",
                "last_name",
            ]
        )
        for user in users:
            # Replace user.password with the actual plaintext password if available
            # If not available, this will be blank or you need to update your user creation logic
            writer.writerow(
                [
                    user.id,
                    user.studentnumber,
                    user.email,
                    getattr(user, "plain_password", ""),
                    user.role,
                    user.first_name,
                    user.last_name,
                ]
            )
    # Encrypt and delete CSV
    export_and_encrypt_csv(csv_filename, zip_filename, password)
    # flash('Accounts exported and encrypted ZIP created.', 'success')
    return redirect(url_for("admin.csv_exports"))


try:
    from flaskr.website import csrf
except ImportError:
    csrf = None

    # ... (other code remains unchanged) ...

    # Place this block after batch_create_accounts is defined (after line 450+)
    pass


# Admin-only decorator
def admin_required(f):
    """
    Decorator to ensure only users with admin role can access the route.
    Must be used after @login_required.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))

        if current_user.role != "admin":
            # flash("Access denied. Admin privileges required.", "error")

            # Redirect based on user role to their appropriate dashboard
            if current_user.role == "teacher":
                return redirect(url_for("views.teacher_dashboard"))
            elif current_user.role == "student":
                return redirect(url_for("views.student_dashboard"))
            else:
                # Fallback to home for any other role
                return redirect(url_for("views.home"))

        return f(*args, **kwargs)

    return decorated_function


def verify_admin_access():
    """
    Helper function to verify admin access.
    Returns True if current user is admin, False otherwise.
    """
    if not current_user.is_authenticated:
        return False
    return current_user.role == "admin"


# Make verify_admin_access available in templates
@admin.app_template_global()
def is_admin():
    """Template function to check if current user is admin"""
    return verify_admin_access()


# Route to handle unauthorized access
@admin.route("/admin/unauthorized")
def unauthorized():
    """Handle unauthorized access attempts"""
    # flash("Access denied. Admin privileges required.", "error")

    # Redirect based on user role if authenticated
    if current_user.is_authenticated:
        if current_user.role == "teacher":
            return redirect(url_for("views.teacher_dashboard"))
        elif current_user.role == "student":
            return redirect(url_for("views.student_dashboard"))

    # Fallback to home
    return redirect(url_for("views.home"))


# Simple form for CSRF protection
class AssignStudentForm(FlaskForm):
    pass


# Password change form
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired("Password is required"),
            Length(min=6, message="Password must be at least 6 characters"),
        ],
    )


class EditAccountForm(FlaskForm):
    studentnumber = IntegerField(
        "Student Number",
        validators=[
            DataRequired("Student number is required"),
            NumberRange(
                min=10000000, max=99999999, message="Student number must be 8 digits"
            ),
        ],
    )
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired("First name is required"),
            Length(min=1, max=50, message="First name must be 1-50 characters"),
        ],
    )
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired("Last name is required"),
            Length(min=1, max=50, message="Last name must be 1-50 characters"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email("Invalid email address"),
            Length(max=100, message="Email must be less than 100 characters"),
        ],
    )

# Account creation form
class CreateAccountForm(FlaskForm):
    studentnumber = IntegerField(
        "Student Number",
        validators=[
            DataRequired("Student number is required"),
            NumberRange(
                min=10000000, max=99999999, message="Student number must be 8 digits"
            ),
        ],
    )
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired("First name is required"),
            Length(min=1, max=50, message="First name must be 1-50 characters"),
        ],
    )
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired("Last name is required"),
            Length(min=1, max=50, message="Last name must be 1-50 characters"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email("Invalid email address"),
            Length(max=100, message="Email must be less than 100 characters"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired("Password is required"),
            Length(min=6, message="Password must be at least 6 characters"),
        ],
    )
    role = SelectField(
        "Role",
        choices=[("student", "Student"), ("teacher", "Teacher"), ("admin", "Admin")],
        validators=[DataRequired("Role is required")],
    )


# Before request handler for admin blueprint
@admin.before_request
def require_admin():
    """
    Ensure all admin routes require admin access.
    This runs before every request to admin routes.
    """
    # Allow unauthorized route for redirect purposes
    if request.endpoint == "admin.unauthorized":
        return

    # Check if user is authenticated
    if not current_user.is_authenticated:
        # flash("Please log in to access admin pages.", "error")
        return redirect(url_for("auth.login"))

    # Check if user has admin role - redirect to their appropriate page
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")

        # Redirect based on user role to their appropriate dashboard
        if current_user.role == "teacher":
            return redirect(url_for("views.teacher_dashboard"))
        elif current_user.role == "student":
            return redirect(url_for("views.student_dashboard"))
        else:
            # Fallback to home for any other role
            return redirect(url_for("views.home"))


@admin.route("/admin")
@login_required
def admin_dashboard():
    # Admin access already verified by before_request handler
    teachers = User.query.filter_by(role=UserRole.TEACHER.value).all()
    students = User.query.filter_by(role=UserRole.STUDENT.value).all()
    admins = User.query.filter_by(role=UserRole.ADMIN.value).all()

    # Create response with no-cache headers to prevent browser caching
    response = make_response(
        render_template(
            "admin/admin.html",
            teachers=teachers,
            students=students,
            admins=admins,
            current_user_id=current_user.id,
        )
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# User profile dispatcher: redirects to the correct profile view
@admin.route("/admin/user/<int:user_id>", methods=["GET", "POST"])
@login_required
def user_profile(user_id):
    # Only admins can access user profiles
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    if user.is_teacher():
        return redirect(url_for("admin.teacher_profile", user_id=user.id))
    elif user.is_student():
        return redirect(url_for("admin.student_profile", user_id=user.id))
    else:
        # flash("Admin profile view not implemented.", "info")
        return redirect(url_for("admin.admin_dashboard"))


# Teacher profile view (for teachers only)
@admin.route("/admin/teacher_profile/<int:user_id>", methods=["GET", "POST"])
@login_required
def teacher_profile(user_id):
    # Only admins can access teacher profiles
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    students = []
    form = AssignStudentForm()
    password_form = ChangePasswordForm()
    edit_form = EditAccountForm()
    if user.is_teacher():
        students = User.query.filter_by(role=UserRole.STUDENT.value).all()

    is_curr_user = user.id == current_user.id

    return render_template(
        "admin/teacher_profile.html",
        user=user,
        students=students,
        form=form,
        edit_form=edit_form,
        password_form=password_form,
        is_curr_user=is_curr_user,
    )


# Route to assign a student to a teacher
@admin.route("/admin/assign_student", methods=["POST"])
@login_required
def assign_student():
    # Only admins can assign students
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))
    teacher_id = int(request.form["teacher_id"])
    student_id = int(request.form["student_id"])
    teacher = User.query.get_or_404(teacher_id)
    student = User.query.get_or_404(student_id)
    if student not in teacher.students:
        teacher.students.append(student)
        db.session.commit()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            # Return student info for live update
            return jsonify(
                success=True,
                message="Student assigned successfully!",
                student={
                    "id": student.id,
                    "name": student.get_full_name(),
                    "email": student.email,
                    "studentnumber": student.studentnumber,
                    "teacher_id": teacher.id,
                },
                csrf_token=request.form.get("csrf_token"),
            )
        # flash("Student assigned successfully!", "success")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=False, message="Student already assigned!")
        # flash("Student already assigned!", "warning")
    return redirect(url_for("admin.teacher_profile", user_id=teacher_id))


# Route to unassign a student from a teacher
@admin.route("/admin/unassign_student", methods=["POST"])
@login_required
def unassign_student():
    # Only admins can unassign students
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))
    teacher_id = int(request.form["teacher_id"])
    student_id = int(request.form["student_id"])
    teacher = User.query.get_or_404(teacher_id)
    student = User.query.get_or_404(student_id)
    if student in teacher.students:
        teacher.students.remove(student)
        db.session.commit()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=True, message="Student unassigned successfully!")
        # flash("Student unassigned successfully!", "success")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(success=False, message="Student was not assigned!")
        flash("Student was not assigned!", "warning")
    return redirect(url_for("admin.teacher_profile", user_id=teacher_id))


# Route to change user password
@admin.route("/admin/change_password/<int:user_id>", methods=["POST"])
@login_required
def change_password(user_id):
    # Only admins can change passwords
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        user.set_password(password_form.new_password.data)
        db.session.commit()
        # flash(f"Password updated successfully for {user.get_full_name()}!", "success")
    else:
        pass
        # flash("Password change failed. Please check the requirements.", "error")

    # Redirect back to appropriate profile
    if user.is_teacher():
        return redirect(url_for("admin.teacher_profile", user_id=user_id))
    else:
        return redirect(url_for("admin.student_profile", user_id=user_id))


# Student profile route
@admin.route("/admin/student/<int:user_id>")
@login_required
@admin_required
def student_profile(user_id):
    # Only admins can access student profiles
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    password_form = ChangePasswordForm()
    edit_form = EditAccountForm()
    # Ensure teachers is a list, not a query
    assigned_teachers = (
        user.teachers.all() if hasattr(user.teachers, "all") else list(user.teachers)
    )
    # Get all teachers for the assign modal
    all_teachers = User.query.filter_by(role=UserRole.TEACHER.value).all()
    return render_template(
        "admin/student_profile.html",
        user=user,
        password_form=password_form,
        edit_form=edit_form,
        assigned_teachers=assigned_teachers,
        all_teachers=all_teachers,
    )


# Account creation route
@admin.route("/admin/create_account", methods=["GET", "POST"])
@login_required
def create_account():
    # Only admins can create accounts
    if current_user.role != "admin":
      # ("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    form = CreateAccountForm()

    if form.validate_on_submit():
        # Check for duplicate student number
        if form.studentnumber.data:
            existing_student_num = User.query.filter_by(
                studentnumber=form.studentnumber.data
            ).first()
            if existing_student_num:
                flash(
                    f"Student number {form.studentnumber.data} already exists.", "error"
                )
                return render_template("admin/account_create.html", form=form)

        # Check for duplicate email if provided
        if form.email.data:
            existing_email = User.query.filter_by(email=form.email.data).first()
            if existing_email:
                flash(f"Email {form.email.data} already exists.", "error")
                return render_template("admin/account_create.html", form=form)

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

        import time

        try:
            # Export account info with plaintext password to CSV before hashing
            export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
            os.makedirs(export_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d")
            export_filename = f"created_accounts_{timestamp}.csv"
            export_path = os.path.join(export_dir, export_filename)
            write_header = not os.path.exists(export_path)
            with open(export_path, "a", newline="", encoding="utf-8") as csvfile:
                import csv

                writer = csv.writer(csvfile)
                if write_header:
                    writer.writerow(
                        [
                            "studentnumber",
                            "first_name",
                            "last_name",
                            "email",
                            "password",
                            "role",
                        ]
                    )
                writer.writerow(
                    [
                        form.studentnumber.data or "",
                        form.first_name.data,
                        form.last_name.data,
                        email,
                        form.password.data,
                        form.role.data,
                    ]
                )
            # Create new user
            new_user = User(
                studentnumber=form.studentnumber.data,
                email=email,
                role=form.role.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                created_at=datetime.now(),
                is_active=True,
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            # flash(f'Account created successfully for {new_user.get_full_name()} ({email}) - Role: {new_user.role.title()}', 'success')
            return redirect(url_for("admin.admin_dashboard"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating account: {str(e)}", "error")
            return render_template("admin/account_create.html", form=form)
    return render_template("admin/account_create.html", form=form)


# Batch account creation endpoint
@admin.route("/admin/batch_create_accounts", methods=["POST"])
@login_required
def batch_create_accounts():
    global _last_created_csv_path
    # print("DEBUGSADASD: ", request.get_json(force=True) or {})
    # print("[DEBUG] batch_create_accounts called by:", current_user.email)
    if current_user.role != "admin":
        # print("[DEBUG] Access denied: not admin")
        return jsonify(success=False, message="Admin privileges required."), 403
    data = request.get_json()
    # print("[DEBUG] Received data:", data)
    accounts = data.get("accounts", [])
    # print(f"[DEBUG] Number of accounts to create: {len(accounts)}")
    created_emails = []
    errors = []
    import time

    created_accounts_for_csv = []

    for acc in accounts:
        # print("[DEBUG] Processing account:", acc)
        # Check for required fields
        role = acc.get("role")
        first_name = acc.get("first_name")
        last_name = acc.get("last_name")
        email = acc.get("email")
        password = acc.get("password")
        studentnumber = acc.get("studentnumber")
        if not (role and first_name and last_name and email and password):
            # print(
            #     f"[DEBUG] Missing fields for {email or '[no email]'}: role={role}, first_name={first_name}, last_name={last_name}, email={email}, password={'yes' if password else 'no'}"
            # )
            errors.append(f"Missing fields for {email or '[no email]' }.")
            continue
        if role == "student":
            if not studentnumber:
                # print(f"[DEBUG] Student number missing for {email}")
                errors.append(f"Student number required for {email}.")
                continue
        # Check for duplicates
        if User.query.filter_by(email=email).first():
            # print(f"[DEBUG] Duplicate email: {email}")
            errors.append(f"Email {email} already exists.")
            continue
        if (
            role == "student"
            and User.query.filter_by(studentnumber=studentnumber).first()
        ):
            # print(f"[DEBUG] Duplicate student number: {studentnumber}")
            errors.append(f"Student number {studentnumber} already exists.")
            continue
        try:
            new_user = User(
                email=email,
                role=role,
                first_name=first_name,
                last_name=last_name,
                created_at=datetime.now(),
                is_active=True,
            )
            # Only set studentnumber if role is student and value is present
            if role == "student" and studentnumber:
                new_user.studentnumber = studentnumber
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            # print(f"[DEBUG] Created user: {email}")
            created_emails.append(email)
            # Add to CSV export list
            created_accounts_for_csv.append(
                {
                    "studentnumber": studentnumber or "",
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": password,
                    "role": role,
                }
            )
        except Exception as e:
            db.session.rollback()
            # print(f"[DEBUG] Error creating {email}: {str(e)}")
            errors.append(f"Error creating {email}: {str(e)}")
    if created_emails:
        # Export created accounts to CSV in exports folder with timestamp
        import csv

        export_dir = os.path.join(os.path.dirname(__file__), "..", "exports")
        os.makedirs(export_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        export_filename = f"created_accounts_{timestamp}.csv"
        export_path = os.path.join(export_dir, export_filename)
        _last_created_csv_path = export_path
        with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
            num_accounts = len(created_accounts_for_csv)
            now = time.localtime()
            date_str = time.strftime("%d/%m/%Y", now)
            time_str = time.strftime("%H:%M:%S", now)
            csvfile.write(f"{num_accounts} accounts created, {date_str}, {time_str}\n")
            fieldnames = [
                "studentnumber",
                "first_name",
                "last_name",
                "email",
                "password",
                "role",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in created_accounts_for_csv:
                writer.writerow(row)
        msg = f"Created accounts: {', '.join(created_emails)}."
        if errors:
            msg += "<br>Some errors: " + "<br>".join(errors)
        # print(f"[DEBUG] Success: {msg}")
        return jsonify(success=True, message=msg, created_emails=created_emails)
    return (
        jsonify(success=False, message="<br>Some errors: " + "<br>".join(errors)),
        400,
    )


# Account creation success page to prevent browser back issues
@admin.route("/admin/account_creation_success/<int:user_id>")
@login_required
def account_creation_success(user_id):
    # Only admins can access account creation success page
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user = User.query.get_or_404(user_id)
    return render_template("admin/account_success.html", user=user)


# Delete user account route
@admin.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    # Only admins can delete accounts
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    user_to_delete = User.query.get_or_404(user_id)

    # Prevent admin from deleting themselves
    if user_to_delete.id == current_user.id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        # Store user info for flash message before deletion
        user_name = user_to_delete.get_full_name()
        user_role = user_to_delete.role

        # If deleting a teacher, unassign all their students first
        if user_to_delete.role == "teacher":
            # Prevent deletion if teacher owns any scenarios
            if user_to_delete.created_scenarios:
                owned_count = len(user_to_delete.created_scenarios)
                if owned_count > 0:
                    flash(
                        f"Cannot delete teacher: assigned as owner of {owned_count} scenario(s). Reassign or delete those scenarios first.",
                        "error",
                    )
                    return redirect(url_for("admin.admin_dashboard"))
            for student in user_to_delete.students.all():
                user_to_delete.students.remove(student)

        # If deleting a student, remove all their scenario assignments
        if user_to_delete.role == "student":
            from .models import StudentScenario

            student_scenarios = StudentScenario.query.filter_by(
                student_id=user_to_delete.id
            ).all()
            for ss in student_scenarios:
                db.session.delete(ss)

        # Delete the user
        db.session.delete(user_to_delete)
        db.session.commit()

        # flash(f"Successfully deleted {user_role} account: {user_name}", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting account: {str(e)}", "error")

    return redirect(url_for("admin.admin_dashboard"))


# Route to handle CSV upload for batch account creation
@admin.route("/admin/upload_accounts_csv", methods=["POST"])
@login_required
def upload_accounts_csv():
    if current_user.role != "admin":
        # flash("Access denied. Admin privileges required.", "error")
        return redirect(url_for("views.home"))

    file = request.files.get("csv_file")
    if not file or file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("admin.create_account"))

    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)

        headers = reader.fieldnames
        clean_headers = [re.sub(r"[^a-z]", "", h.lower()) for h in headers]
        indices = {
            "email": -1,
            "stuno": -1,
            "pword": -1,
            "fname": -1,
            "lname": -1,
        }
        for i, h in enumerate(clean_headers):
            if "mail" in h:  # email
                indices["email"] = i
            elif "student" in h:  # student number
                indices["stuno"] = i
            elif "p" in h:  # password
                indices["pword"] = i
            elif "f" in h:  # first name
                indices["fname"] = i
            else:  # last name
                indices["lname"] = i

        accounts = []
        for row in reader:
            stuno = (
                row[headers[indices["stuno"]]].strip() if indices["stuno"] != -1 else ""
            )
            fname = (
                row[headers[indices["fname"]]].strip() if indices["fname"] != -1 else ""
            )
            lname = (
                row[headers[indices["lname"]]].strip() if indices["lname"] != -1 else ""
            )
            email = (
                row[headers[indices["email"]]].strip() if indices["email"] != -1 else ""
            )
            pword = (
                row[headers[indices["pword"]]].strip() if indices["pword"] != -1 else ""
            )

            role = "student" if stuno else "teacher"
            accounts.append(
                {
                    "role": role,
                    "studentnumber": stuno,
                    "first_name": fname,
                    "last_name": lname,
                    "email": email,
                    "password": pword,
                }
            )
        return jsonify(success=True, accounts=accounts)
    except Exception as e:
        return jsonify(success=False, message=f"Error processing CSV file: {str(e)}")


# Exempt the batch_create_accounts and upload_accounts_csv routes from CSRF protection using the csrf instance
try:
    from flaskr.website import csrf

    csrf.exempt(batch_create_accounts)
    csrf.exempt(upload_accounts_csv)
except ImportError:
    pass

# Exempt the batch_create_accounts route from CSRF protection using the csrf instance
try:
    from flaskr.website import csrf

    csrf.exempt(batch_create_accounts)
except ImportError:
    pass


@admin.route("/admin/export_all_students_csv")
@login_required
def export_all_students_csv():
    if current_user.role != "admin":
        return "Access denied", 403

    # --- STUDENT DATA SHEET ---
    students = User.query.filter_by(role="student").all()
    student_rows = []
    for student in students:
        student_rows.append(
            {
                "studentnumber": student.studentnumber,
                "email": student.email,
                "first_name": student.first_name,
                "last_name": student.last_name,
            }
        )
    df_students = pd.DataFrame(student_rows)

    # --- SCENARIOS SHEET ---
    scenario_rows = []
    for student in students:
        student_scenarios = (
            StudentScenario.query.join(Scenario)
            .filter(StudentScenario.student_id == student.id)
            .all()
        )

        for student_scenario in student_scenarios:
            scenario_patient = ScenarioPatient.query.filter_by(
                scenario_id=student_scenario.scenario_id, student_id=student.id
            ).first()

            if scenario_patient is None:
                continue
            patient = Patient.query.get(scenario_patient.patient_id)
            if patient is None:
                continue

            scenario = Scenario.query.get(student_scenario.scenario_id)
            if scenario is None:
                continue

            # print("Patient =", patient)
            # print("Scenario =", scenario)
            prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()

            presc_data = []
            for prescription in prescriptions:
                presc_data.append(
                    {
                        "drug_name": prescription.drug_name,
                        "dose_instr": prescription.dose_instr,
                        "dose_qty": prescription.dose_qty,
                        "dose_rpt": prescription.dose_rpt,
                        "prescribed_date": prescription.prescribed_date,
                        "dispensed_date": prescription.dispensed_date,
                        "remaining_repeats": prescription.remaining_repeats,
                        "paperless": prescription.paperless,
                        "brand_sub_not_prmt": prescription.brand_sub_not_prmt,
                        "dispensed_at_this_pharmacy": prescription.dispensed_at_this_pharmacy,
                        "prescriber_id": prescription.prescriber_id,
                        "prescriber_name": (
                            f"{prescription.prescriber.fname} {prescription.prescriber.lname}"
                            if prescription.prescriber
                            else None
                        ),
                    }
                )

            scenario_rows.append(
                {
                    # Student info
                    "studentnumber": student.studentnumber if student else None,
                    # Scenario info
                    "scenario_name": scenario.name,
                    "scenario_version": scenario.version,
                    "assigned_at": student_scenario.assigned_at,
                    "submitted_at": student_scenario.submitted_at,
                    "completed_at": student_scenario.completed_at,
                    "score": student_scenario.score,
                    "status": student_scenario.status,
                    # Patient info
                    "patient_id": patient.id if patient else None,
                    "patient_last_name": patient.last_name if patient else None,
                    "patient_given_name": patient.given_name if patient else None,
                    "patient_dob": patient.dob if patient else None,
                    # Prescription data
                    "prescriptions": presc_data,
                }
            )
    df_scenarios = pd.DataFrame(scenario_rows)

    # --- WRITE XLSX IN MEMORY ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_students.to_excel(writer, sheet_name="Students", index=False)
        df_scenarios.to_excel(writer, sheet_name="Scenarios", index=False)
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="full_student_export.xlsx",
    )
