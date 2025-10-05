from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    request,
    current_app,
    send_file,
    send_from_directory,
)
from flask_login import login_required, current_user
from .models import (
    db,
    Patient,
    Prescriber,
    Prescription,
    PrescriptionStatus,
    ASLStatus,
    ASL,
    Scenario,
    User,
    StudentScenario,
    ScenarioPatient,
    Submission,
)
from .forms import PatientForm, ASLForm, DeleteForm, EmptyForm
from sqlalchemy import or_
from .converters import ingest_pt_data_contract
from datetime import datetime
from functools import wraps
import requests
import os
from pathlib import Path
from werkzeug.utils import secure_filename

# Optional import for readme rendering
try:
    from render_readme import render_readme
except ImportError:

    def render_readme(*args, **kwargs):
        return "Readme rendering not available"


views = Blueprint("views", __name__)


# Helper decorator to require teacher role
def teacher_required(f):
    """Decorator to require teacher role"""

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_teacher():
            # flash("You need to be a teacher to access this page", "error")
            return redirect(url_for("auth.home"))
        return f(*args, **kwargs)

    return decorated_function


@views.route("/scenarios/<int:scenario_id>")
@login_required
def scenario_dashboard(scenario_id):
    """
    Display scenario dashboard for both teachers and students
    Teachers can see full details and management options
    Students can see scenario details and access patient ASL
    """
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user has access to this scenario
    if current_user.is_student():
        # Students can only access scenarios assigned to them
        if scenario not in current_user.assigned_scenarios:
            flash("You do not have access to this scenario", "error")
            return redirect(url_for("views.student_dashboard"))
    elif current_user.is_teacher():
        # Teachers can only access scenarios they created
        if scenario.teacher_id != current_user.id:
            flash("You can only access scenarios you created", "error")
            return redirect(url_for("views.teacher_dashboard"))

    # Get assigned students for this scenario
    assigned_students = (
        User.query.join(StudentScenario)
        .filter(StudentScenario.scenario_id == scenario_id)
        .all()
    )

    # Get scenario patients if any
    scenario_patients = scenario.patient_data

    # Get all available patients for selection
    all_patients = Patient.query.all()

    # Get student scenario assignment if current user is a student
    student_scenario = None
    assigned_patient = None
    if current_user.is_student():
        student_scenario = StudentScenario.query.filter_by(
            student_id=current_user.id, scenario_id=scenario_id
        ).first()

        # Find patient assigned to this student for this scenario
        if student_scenario:
            patient_assignment = ScenarioPatient.query.filter_by(
                scenario_id=scenario_id, student_id=current_user.id
            ).first()

            if patient_assignment:
                assigned_patient = Patient.query.get(patient_assignment.patient_id)
            else:
                # Fallback to scenario's active patient if no individual assignment
                assigned_patient = scenario.active_patient

    return render_template(
        "views/scenario_dashboard.html",
        scenario=scenario,
        assigned_students=assigned_students,
        scenario_patients=scenario_patients,
        all_patients=all_patients,
        student_scenario=student_scenario,
        assigned_patient=assigned_patient,
    )


@views.route("/scenarios/<int:scenario_id>/edit", methods=["GET", "POST"])
@teacher_required
def edit_scenario(scenario_id):
    """Edit scenario details - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher can only edit their own scenarios
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created", "error")
        return redirect(url_for("views.teacher_dashboard"))

    if request.method == "POST":
        scenario.name = request.form.get("name", scenario.name)
        scenario.description = request.form.get("description", scenario.description)
        scenario.password = request.form.get("password") or None
        scenario.updated_at = datetime.now()

        db.session.commit()
        flash("Scenario updated successfully!", "success")
        return redirect(url_for("views.scenario_dashboard", scenario_id=scenario.id))

    return render_template("views/edit_scenario.html", scenario=scenario)


@views.route("/scenarios/<int:scenario_id>/delete", methods=["POST"])
@teacher_required
def delete_scenario(scenario_id):
    """Delete a scenario - teachers only (archive instead of hard delete)"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher can only delete their own scenarios
    if scenario.teacher_id != current_user.id:
        flash("You can only delete scenarios you created", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = DeleteForm()
    if form.validate_on_submit():
        try:
            # Archive instead of hard delete to preserve data integrity
            scenario.is_archived = True
            scenario.updated_at = datetime.now()

            db.session.commit()
            flash(
                f'Scenario "{scenario.name}" has been archived successfully!', "success"
            )
        except Exception as e:
            db.session.rollback()
            flash(
                "An error occurred while archiving the scenario. Please try again.",
                "error",
            )
    else:
        flash("Invalid request. Please try again.", "error")

    return redirect(url_for("views.teacher_dashboard"))


@views.route("/scenarios/<int:scenario_id>/assign", methods=["GET", "POST"])
@teacher_required
def assign_scenario(scenario_id):
    """Assign scenario to students - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher can only assign their own scenarios
    if scenario.teacher_id != current_user.id:
        flash("You can only assign scenarios you created", "error")
        return redirect(url_for("views.teacher_dashboard"))

    if request.method == "POST":
        # Check if we're handling individual patient assignments
        assignments_data = {}
        for key, value in request.form.items():
            if key.startswith("assignments[") and key.endswith("][student_id]"):
                index = key.split("[")[1].split("]")[0]
                if index not in assignments_data:
                    assignments_data[index] = {}
                assignments_data[index]["student_id"] = value
            elif key.startswith("assignments[") and key.endswith("][patient_id]"):
                index = key.split("[")[1].split("]")[0]
                if index not in assignments_data:
                    assignments_data[index] = {}
                assignments_data[index]["patient_id"] = value

        if assignments_data:
            # Handle individual patient assignments
            # Clear existing assignments if requested
            if request.form.get("clear_existing") == "true":
                StudentScenario.query.filter_by(scenario_id=scenario.id).delete()
                ScenarioPatient.query.filter_by(scenario_id=scenario.id).delete()

            success_count = 0
            errors = []

            # Get already assigned patients in this scenario
            already_assigned_patients = set()
            existing_patient_assignments = ScenarioPatient.query.filter_by(
                scenario_id=scenario.id
            ).all()
            for assignment in existing_patient_assignments:
                already_assigned_patients.add(assignment.patient_id)

            for assignment in assignments_data.values():
                student_id = assignment.get("student_id")
                patient_id = assignment.get("patient_id")

                if student_id and patient_id:
                    student = User.query.filter_by(
                        id=student_id, role="student"
                    ).first()
                    patient = Patient.query.get(patient_id)

                    if student and patient:
                        # Check if this patient is already assigned to another student in this scenario
                        existing_patient_assignment = (
                            ScenarioPatient.query.filter_by(
                                scenario_id=scenario.id, patient_id=patient_id
                            )
                            .filter(ScenarioPatient.student_id != student_id)
                            .first()
                        )

                        if existing_patient_assignment:
                            assigned_student = User.query.get(
                                existing_patient_assignment.student_id
                            )
                            patient_name = (
                                f"{patient.title or ''} {patient.given_name or ''} {patient.last_name or ''}".strip()
                                or f"Patient {patient.id}"
                            )
                            errors.append(
                                f"{patient_name} is already assigned to {assigned_student.get_full_name()}"
                            )
                            continue

                        # Check if student assignment already exists
                        existing_student = StudentScenario.query.filter_by(
                            student_id=student_id, scenario_id=scenario.id
                        ).first()

                        if not existing_student:
                            student_assignment = StudentScenario(
                                student_id=student_id, scenario_id=scenario.id
                            )
                            db.session.add(student_assignment)

                        # Check if this exact patient assignment already exists
                        existing_patient = ScenarioPatient.query.filter_by(
                            student_id=student_id,
                            scenario_id=scenario.id,
                            patient_id=patient_id,
                        ).first()

                        if not existing_patient:
                            # Remove any existing patient assignment for this student in this scenario
                            ScenarioPatient.query.filter_by(
                                student_id=student_id, scenario_id=scenario.id
                            ).delete()

                            patient_assignment = ScenarioPatient(
                                student_id=student_id,
                                scenario_id=scenario.id,
                                patient_id=patient_id,
                            )
                            db.session.add(patient_assignment)

                        success_count += 1

            db.session.commit()

            if errors:
                flash(
                    f'Assignment completed with warnings: {"; ".join(errors)}',
                    "warning",
                )
            else:
                flash(
                    f"Successfully assigned {success_count} students with their patients!",
                    "success",
                )
        else:
            # Handle simple student assignments (fallback for old method)
            student_ids = request.form.getlist("student_ids")

            # Clear existing assignments if requested
            if request.form.get("clear_existing") == "true":
                StudentScenario.query.filter_by(scenario_id=scenario.id).delete()

            # Add new assignments
            for student_id in student_ids:
                student = User.query.filter_by(id=student_id, role="student").first()
                if student:
                    # Check if assignment already exists
                    existing = StudentScenario.query.filter_by(
                        student_id=student_id, scenario_id=scenario.id
                    ).first()

                    if not existing:
                        assignment = StudentScenario(
                            student_id=student_id, scenario_id=scenario.id
                        )
                        db.session.add(assignment)

            db.session.commit()
            flash(f"Scenario assigned to {len(student_ids)} students!", "success")

        return redirect(url_for("views.scenario_dashboard", scenario_id=scenario.id))

    # GET request - show assignment form
    students = User.query.filter_by(role="student", is_active=True).all()
    assigned_student_ids = [s.id for s in scenario.assigned_students]
    available_patients = Patient.query.all()  # Get all patients for assignment

    # Get current patient assignments for this scenario
    current_assignments = {}
    assigned_patients = set()
    scenario_patient_assignments = ScenarioPatient.query.filter_by(
        scenario_id=scenario.id
    ).all()

    for assignment in scenario_patient_assignments:
        current_assignments[assignment.student_id] = assignment.patient_id
        assigned_patients.add(assignment.patient_id)

    return render_template(
        "views/assign_scenario.html",
        scenario=scenario,
        students=students,
        assigned_student_ids=assigned_student_ids,
        available_patients=available_patients,
        current_assignments=current_assignments,
        assigned_patients=assigned_patients,
    )


@views.route("/scenarios/<int:scenario_id>/assign-patient", methods=["GET", "POST"])
@teacher_required
def assign_patient_to_scenario(scenario_id):
    """Assign a patient to a scenario - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher can only modify their own scenarios
    if scenario.teacher_id != current_user.id:
        flash("You can only modify scenarios you created", "error")
        return redirect(url_for("views.teacher_dashboard"))

    if request.method == "POST":
        patient_id = request.form.get("patient_id")

        if patient_id:
            # Check if patient is already assigned
            existing = ScenarioPatient.query.filter_by(
                scenario_id=scenario.id, patient_id=patient_id
            ).first()

            if not existing:
                scenario_patient = ScenarioPatient(
                    scenario_id=scenario.id, patient_id=patient_id
                )
                db.session.add(scenario_patient)
                db.session.commit()
                flash("Patient assigned to scenario successfully!", "success")
            else:
                flash("Patient is already assigned to this scenario", "info")
        else:
            flash("Please select a patient", "error")

        return redirect(url_for("views.scenario_dashboard", scenario_id=scenario.id))

    # GET request - show patient selection form
    patients = Patient.query.filter_by(is_registered=True).all()
    assigned_patient_ids = [sp.patient_id for sp in scenario.patient_data]

    return render_template(
        "views/assign_patient.html",
        scenario=scenario,
        patients=patients,
        assigned_patient_ids=assigned_patient_ids,
    )


@views.route("/scenarios/<int:scenario_id>/duplicate", methods=["POST"])
@teacher_required
def duplicate_scenario(scenario_id):
    """Duplicate a scenario - teachers only"""
    original_scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher can only duplicate their own scenarios
    if original_scenario.teacher_id != current_user.id:
        flash("You can only duplicate scenarios you created", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        try:
            # Create new scenario
            new_scenario = Scenario(
                name=f"{original_scenario.name} (Copy)",
                description=original_scenario.description,
                teacher_id=current_user.id,
                password=original_scenario.password,
                question_text=original_scenario.question_text,
                active_patient_id=original_scenario.active_patient_id,
                version=1,
                parent_scenario_id=original_scenario.id,
            )

            db.session.add(new_scenario)
            db.session.flush()  # Get the ID

            # Copy patient data associations
            for patient_data in original_scenario.patient_data:
                new_patient_data = ScenarioPatient(
                    scenario_id=new_scenario.id, patient_id=patient_data.patient_id
                )
                db.session.add(new_patient_data)

            db.session.commit()
            flash("Scenario duplicated successfully!", "success")
            return redirect(
                url_for("views.scenario_dashboard", scenario_id=new_scenario.id)
            )

        except Exception as e:
            db.session.rollback()
            flash("Error duplicating scenario. Please try again.", "error")
    else:
        flash("Invalid request. Please try again.", "error")

    return redirect(url_for("views.teacher_dashboard"))


@views.route("/")
def index():
    """Root route - redirects to appropriate dashboard"""
    if current_user.is_authenticated:
        if current_user.is_teacher():
            return redirect(url_for("views.teacher_dashboard"))
        else:
            return redirect(url_for("views.student_dashboard"))
    return redirect(url_for("auth.login"))


# Teacher Dashboard
@views.route("/teacher/dashboard")
@teacher_required
def teacher_dashboard():
    """Teacher dashboard showing all scenarios"""
    # Get teacher's scenarios
    scenarios = (
        Scenario.query.filter_by(teacher_id=current_user.id, is_archived=False)
        .order_by(Scenario.created_at.desc())
        .all()
    )

    # Get some stats
    total_scenarios = len(scenarios)
    total_students = User.query.filter_by(role="student").count()
    total_patients = Patient.query.count()

    # Add submission counts and grading statistics to each scenario
    for scenario in scenarios:
        # Count submissions for this scenario by counting submitted StudentScenarios
        submitted_count = (
            StudentScenario.query.filter_by(scenario_id=scenario.id)
            .filter(StudentScenario.status.in_(["submitted", "graded"]))
            .count()
        )

        # Count graded submissions
        graded_count = StudentScenario.query.filter_by(
            scenario_id=scenario.id, status="graded"
        ).count()

        # Count total assigned students
        total_assigned = StudentScenario.query.filter_by(
            scenario_id=scenario.id
        ).count()

        # Get all submissions for this scenario
        scenario_submissions = (
            db.session.query(Submission)
            .join(StudentScenario)
            .filter(StudentScenario.scenario_id == scenario.id)
            .all()
        )

        # Add the counts as attributes
        scenario.submission_count = submitted_count
        scenario.submissions = scenario_submissions
        scenario.graded_count = graded_count
        scenario.total_assigned = total_assigned

    # Create forms
    form = EmptyForm()
    delete_form = DeleteForm()

    return render_template(
        "views/teacher_dash.html",
        scenarios=scenarios,
        total_scenarios=total_scenarios,
        total_students=total_students,
        total_patients=total_patients,
        form=form,
        delete_form=delete_form,
    )


@views.route("/student/dashboard")
@login_required
def student_dashboard():
    """Student dashboard showing assigned scenarios"""
    if current_user.is_teacher():
        return redirect(url_for("views.teacher_dashboard"))

    # Get student's assigned scenarios with submission status
    student_scenarios = StudentScenario.query.filter_by(
        student_id=current_user.id
    ).all()

    # Get detailed information for each scenario
    scenario_data = []
    for ss in student_scenarios:
        scenario = Scenario.query.get(ss.scenario_id)

        # Find patient assigned to this student for this scenario
        patient_assignment = ScenarioPatient.query.filter_by(
            scenario_id=scenario.id, student_id=current_user.id
        ).first()

        assigned_patient = None
        if patient_assignment:
            assigned_patient = Patient.query.get(patient_assignment.patient_id)
        else:
            # Fallback to scenario's active patient if no individual assignment
            assigned_patient = scenario.active_patient

        # Get submission status
        submissions = (
            Submission.query.filter_by(student_scenario_id=ss.id).all()
            if assigned_patient
            else []
        )

        scenario_data.append(
            {
                "student_scenario": ss,
                "scenario": scenario,
                "patient": assigned_patient,
                "submissions": submissions,
                "can_submit": assigned_patient is not None
                and ss.status in ["assigned", "submitted"],
            }
        )

    return render_template("views/student_dash.html", scenario_data=scenario_data)


@views.route("/students/manage")
@teacher_required
def student_management():
    """Student management dashboard for teachers"""
    try:
        # Get all students
        students = User.query.filter_by(role="student").all()

        # Calculate stats
        active_students = 0
        total_assignments = 0

        for student in students:
            # Check if student has assigned_scenarios attribute
            if hasattr(student, "assigned_scenarios") and student.assigned_scenarios:
                student_scenarios = student.assigned_scenarios
                if len(student_scenarios) > 0:
                    active_students += 1
                total_assignments += len(student_scenarios)

                # Add completed scenarios count
                student.completed_scenarios = [
                    ss
                    for ss in student_scenarios
                    if hasattr(ss, "status") and ss.status == "graded"
                ]
            else:
                student.completed_scenarios = []

        return render_template(
            "views/student_management.html",
            students=students,
            active_students=active_students,
            total_assignments=total_assignments,
        )
    except Exception as e:
        print(f"Error in student_management: {str(e)}")
        import traceback

        traceback.print_exc()
        flash(f"Error loading student management: {str(e)}", "error")
        return redirect(url_for("views.teacher_dashboard"))


@views.route("/students/add", methods=["POST"])
@teacher_required
def add_student():
    """Add a new student to the system"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["email", "password", "first_name", "last_name"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": f'{field.replace("_", " ").title()} is required',
                        }
                    ),
                    400,
                )

        # Check if email already exists
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user:
            return jsonify({"success": False, "message": "Email already exists"}), 400

        # Create new student user
        new_student = User(
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            role="student",
        )

        # Set password
        new_student.set_password(data["password"])

        db.session.add(new_student)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Student added successfully",
                "student": {
                    "id": new_student.id,
                    "email": new_student.email,
                    "first_name": new_student.first_name,
                    "last_name": new_student.last_name,
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/students/<int:student_id>/edit", methods=["POST"])
@teacher_required
def edit_student(student_id):
    """Edit student details"""
    try:
        student = User.query.filter_by(id=student_id, role="student").first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404

        data = request.get_json()

        # Update fields if provided
        if data.get("first_name"):
            student.first_name = data["first_name"]
        if data.get("last_name"):
            student.last_name = data["last_name"]
        if data.get("email"):
            # Check if new email is unique
            existing = User.query.filter(
                User.email == data["email"], User.id != student_id
            ).first()
            if existing:
                return (
                    jsonify({"success": False, "message": "Email already exists"}),
                    400,
                )
            student.email = data["email"]
        if data.get("password"):
            student.set_password(data["password"])

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Student updated successfully",
                "student": {
                    "id": student.id,
                    "email": student.email,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                },
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/students/<int:student_id>/delete", methods=["DELETE"])
@teacher_required
def delete_student(student_id):
    """Delete a student (soft delete - deactivate)"""
    try:
        student = User.query.filter_by(id=student_id, role="student").first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404

        # Option 1: Soft delete - deactivate the student
        student.is_active = False

        # Option 2: Hard delete - remove from database
        # Remove all student scenario assignments first
        # StudentScenario.query.filter_by(student_id=student_id).delete()
        # db.session.delete(student)

        db.session.commit()

        return jsonify({"success": True, "message": "Student deleted successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/students/<int:student_id>/view", methods=["GET"])
@teacher_required
def view_student(student_id):
    """Get detailed student information"""
    try:
        student = User.query.filter_by(id=student_id, role="student").first()
        if not student:
            return jsonify({"success": False, "message": "Student not found"}), 404

        # Get assigned scenarios
        assigned_scenarios = []
        for ss in student.assigned_scenarios:
            scenario = Scenario.query.get(ss.scenario_id)
            if scenario:
                assigned_scenarios.append(
                    {
                        "id": scenario.id,
                        "name": scenario.name,
                        "status": ss.status,
                        "assigned_at": (
                            ss.assigned_at.isoformat() if ss.assigned_at else None
                        ),
                        "submitted_at": (
                            ss.submitted_at.isoformat() if ss.submitted_at else None
                        ),
                    }
                )

        return jsonify(
            {
                "success": True,
                "student": {
                    "id": student.id,
                    "email": student.email,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "created_at": (
                        student.created_at.isoformat()
                        if hasattr(student, "created_at") and student.created_at
                        else None
                    ),
                    "assigned_scenarios": assigned_scenarios,
                    "total_scenarios": len(assigned_scenarios),
                    "completed_scenarios": len(
                        [s for s in assigned_scenarios if s["status"] == "completed"]
                    ),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/students/bulk-delete", methods=["POST"])
@teacher_required
def bulk_delete_students():
    """Delete multiple students at once"""
    try:
        data = request.get_json()
        student_ids = data.get("student_ids", [])

        if not student_ids:
            return jsonify({"success": False, "message": "No students selected"}), 400

        # Soft delete all selected students
        User.query.filter(User.id.in_(student_ids), User.role == "student").update(
            {"is_active": False}, synchronize_session=False
        )

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"{len(student_ids)} student(s) deleted successfully",
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/students/search", methods=["GET"])
@teacher_required
def search_students():
    """Search for students by name or email"""
    try:
        query = request.args.get("q", "")

        if not query:
            students = User.query.filter_by(role="student", is_active=True).all()
        else:
            students = User.query.filter(
                User.role == "student",
                User.is_active == True,
                db.or_(
                    User.first_name.ilike(f"%{query}%"),
                    User.last_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                    User.student_id.ilike(f"%{query}%"),
                ),
            ).all()

        results = []
        for student in students:
            results.append(
                {
                    "id": student.id,
                    "email": student.email,
                    "first_name": student.first_name,
                    "last_name": student.last_name,
                    "student_id": student.student_id,
                    "scenarios_count": (
                        len(student.assigned_scenarios)
                        if hasattr(student, "assigned_scenarios")
                        else 0
                    ),
                }
            )

        return jsonify({"success": True, "students": results, "count": len(results)})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@views.route("/static/js/<path:filename>")
def js_module(filename):
    return send_from_directory("static/js", filename, mimetype="application/javascript")


@views.route("/patients/create", methods=["GET", "POST"])
@teacher_required
def create_patient():
    form = PatientForm()

    if form.validate_on_submit():
        patient = Patient()

        # Basic details
        patient.last_name = form.basic.lastName.data
        patient.given_name = form.basic.givenName.data
        patient.title = form.basic.title.data
        patient.sex = form.basic.sex.data
        patient.dob = (
            form.basic.dob.data.strftime("%d/%m/%Y") if form.basic.dob.data else None
        )
        patient.pt_number = form.basic.ptNumber.data

        # Contact
        patient.address = request.form.get("basic-address")
        patient.suburb = form.basic.suburb.data
        patient.state = form.basic.state.data
        patient.postcode = form.basic.postcode.data
        patient.phone = form.basic.phone.data
        patient.mobile = form.basic.mobile.data
        patient.licence = form.basic.licence.data
        patient.sms_repeats = form.basic.smsRepeats.data
        patient.sms_owing = form.basic.smsOwing.data
        patient.email = form.basic.email.data

        # Medicare
        patient.medicare = form.basic.medicare.data
        patient.medicare_valid_to = form.basic.medicareValidTo.data
        patient.medicare_surname = form.basic.medicareSurname.data
        patient.medicare_given_name = form.basic.medicareGivenName.data

        # Concession
        patient.concession_number = form.basic.concessionNumber.data
        patient.concession_valid_to = (
            form.basic.concessionValidTo.data.strftime("%d/%m/%Y")
            if form.basic.concessionValidTo.data
            else None
        )
        patient.safety_net_number = form.basic.safetyNetNumber.data
        patient.repatriation_number = form.basic.repatriationNumber.data
        patient.repatriation_valid_to = (
            form.basic.repatriationValidTo.data.strftime("%d/%m/%Y")
            if form.basic.repatriationValidTo.data
            else None
        )
        patient.repatriation_type = form.basic.repatriationType.data
        patient.ndss_number = form.basic.ndssNumber.data

        # MyHR
        patient.ihi_number = form.basic.ihiNumber.data
        patient.ihi_status = form.basic.ihiStatus.data
        patient.ihi_record_status = form.basic.ihiRecordStatus.data

        # Doctor + flags
        patient.doctor = form.basic.doctor.data
        patient.ctg_registered = form.basic.ctgRegistered.data
        patient.generics_only = form.basic.genericsOnly.data
        patient.repeats_held = form.basic.repeatsHeld.data
        patient.pt_deceased = form.basic.ptDeceased.data

        db.session.add(patient)
        db.session.commit()

        flash("Patient created successfully!", "success")
        return redirect(url_for("views.patient_dashboard"))

    return render_template("views/edit_pt.html", form=form, patient=None)


@views.route("/patients/edit/<int:patient_id>", methods=["GET", "POST"])
@teacher_required
def edit_pt(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm()

    # --- Prefill form values on GET ---
    if request.method == "GET":
        form.basic.lastName.data = patient.last_name
        form.basic.givenName.data = patient.given_name
        form.basic.title.data = patient.title
        form.basic.sex.data = patient.sex
        form.basic.dob.data = (
            datetime.strptime(patient.dob, "%d/%m/%Y") if patient.dob else None
        )
        form.basic.ptNumber.data = patient.pt_number

        form.basic.suburb.data = patient.suburb
        form.basic.state.data = patient.state
        form.basic.postcode.data = patient.postcode
        form.basic.phone.data = patient.phone
        form.basic.mobile.data = patient.mobile
        form.basic.licence.data = patient.licence
        form.basic.smsRepeats.data = patient.sms_repeats
        form.basic.smsOwing.data = patient.sms_owing
        form.basic.email.data = patient.email

        form.basic.medicare.data = patient.medicare
        form.basic.medicareValidTo.data = patient.medicare_valid_to
        form.basic.medicareSurname.data = patient.medicare_surname
        form.basic.medicareGivenName.data = patient.medicare_given_name

        form.basic.concessionNumber.data = patient.concession_number
        if patient.concession_valid_to:
            form.basic.concessionValidTo.data = datetime.strptime(
                patient.concession_valid_to, "%d/%m/%Y"
            )
        form.basic.safetyNetNumber.data = patient.safety_net_number
        form.basic.repatriationNumber.data = patient.repatriation_number
        if patient.repatriation_valid_to:
            form.basic.repatriationValidTo.data = datetime.strptime(
                patient.repatriation_valid_to, "%d/%m/%Y"
            )
        form.basic.repatriationType.data = patient.repatriation_type
        form.basic.ndssNumber.data = patient.ndss_number

        form.basic.ihiNumber.data = patient.ihi_number
        form.basic.ihiStatus.data = patient.ihi_status
        form.basic.ihiRecordStatus.data = patient.ihi_record_status

        form.basic.doctor.data = patient.doctor
        form.basic.ctgRegistered.data = patient.ctg_registered
        form.basic.genericsOnly.data = patient.generics_only
        form.basic.repeatsHeld.data = patient.repeats_held
        form.basic.ptDeceased.data = patient.pt_deceased

    # --- Save updates on POST ---
    if form.validate_on_submit():
        patient.last_name = form.basic.lastName.data
        patient.given_name = form.basic.givenName.data
        patient.title = form.basic.title.data
        patient.sex = form.basic.sex.data
        patient.dob = (
            form.basic.dob.data.strftime("%d/%m/%Y") if form.basic.dob.data else None
        )
        patient.pt_number = form.basic.ptNumber.data

        patient.address = request.form.get("basic-address")
        patient.suburb = form.basic.suburb.data
        patient.state = form.basic.state.data
        patient.postcode = form.basic.postcode.data
        patient.phone = form.basic.phone.data
        patient.mobile = form.basic.mobile.data
        patient.licence = form.basic.licence.data
        patient.sms_repeats = form.basic.smsRepeats.data
        patient.sms_owing = form.basic.smsOwing.data
        patient.email = form.basic.email.data

        patient.medicare = form.basic.medicare.data
        patient.medicare_issue = form.basic.medicareIssue.data
        patient.medicare_valid_to = form.basic.medicareValidTo.data
        patient.medicare_surname = form.basic.medicareSurname.data
        patient.medicare_given_name = form.basic.medicareGivenName.data

        patient.concession_number = form.basic.concessionNumber.data
        patient.concession_valid_to = (
            form.basic.concessionValidTo.data.strftime("%d/%m/%Y")
            if form.basic.concessionValidTo.data
            else None
        )
        patient.safety_net_number = form.basic.safetyNetNumber.data
        patient.repatriation_number = form.basic.repatriationNumber.data
        patient.repatriation_valid_to = (
            form.basic.repatriationValidTo.data.strftime("%d/%m/%Y")
            if form.basic.repatriationValidTo.data
            else None
        )
        patient.repatriation_type = form.basic.repatriationType.data
        patient.ndss_number = form.basic.ndssNumber.data

        patient.ihi_number = form.basic.ihiNumber.data
        patient.ihi_status = form.basic.ihiStatus.data
        patient.ihi_record_status = form.basic.ihiRecordStatus.data

        patient.doctor = form.basic.doctor.data
        patient.ctg_registered = form.basic.ctgRegistered.data
        patient.generics_only = form.basic.genericsOnly.data
        patient.repeats_held = form.basic.repeatsHeld.data
        patient.pt_deceased = form.basic.ptDeceased.data

        db.session.commit()
        flash("Patient updated successfully!", "success")
        return redirect(url_for("views.patient_dashboard"))

    return render_template("views/edit_pt.html", form=form, patient=patient)


@views.route("/show-users")
def show_users():
    from .models import User

    users = User.query.all()
    return "<br>".join(
        [
            f"ID: {u.id} | Username: {u.username} | Email: {u.email} | Password: {u.password} | Role: {u.role}"
            for u in users
        ]
    )


@views.route("/asl/<int:pt>")
def asl(pt: int):
    """ASL page - now requires login"""
    try:
        patient = Patient.query.get_or_404(pt)

        # Check access control
        can_view_asl = patient.can_view_asl()

        # Only get prescriptions if we have access
        asl_prescriptions = []
        alr_prescriptions = []

        if can_view_asl:
            # Get ALL prescriptions for ASL display (not just available ones)
            # For ASL items - we distinguish them from ALR by having a non-minimal prescriber
            asl_prescriptions = (
                db.session.query(Prescription, Prescriber)
                .join(Prescriber, Prescription.prescriber_id == Prescriber.id)
                .filter(
                    Prescription.patient_id == pt,
                    Prescriber.fname != "ALR",  # Exclude ALR placeholder prescribers
                )
                .all()
            )

            # For ALR items - these have the placeholder ALR prescriber or have remaining repeats
            alr_prescriptions = (
                db.session.query(Prescription, Prescriber)
                .join(Prescriber, Prescription.prescriber_id == Prescriber.id)
                .filter(
                    Prescription.patient_id == pt,
                    db.or_(
                        Prescriber.fname == "ALR",  # ALR placeholder prescribers
                        Prescription.remaining_repeats
                        > 0,  # Or prescriptions with remaining repeats
                    ),
                )
                .all()
            )

        pt_data = {
            "medicare": patient.medicare,
            "pharmaceut-ben-entitlement-no": patient.pharmaceut_ben_entitlement_no,
            "sfty-net-entitlement-cardholder": patient.sfty_net_entitlement_cardholder,
            "rpbs-ben-entitlement-cardholder": patient.rpbs_ben_entitlement_cardholder,
            "name": patient.name,
            "dob": patient.dob,
            "preferred-contact": patient.preferred_contact,
            "address-1": patient.address or "",
            "address-2": "",  # Patient model doesn't have address_2
            "script-date": patient.script_date,
            "pbs": patient.pbs,
            "rpbs": patient.rpbs,
            "consent-status": {
                "is-registered": patient.is_registered,
                "status": patient.get_asl_status().name.replace("_", " ").title(),
                "last-updated": (
                    patient.consent_last_updated
                    if patient.consent_last_updated
                    else "01/Jan/2000 02:59AM"
                ),
            },
            "asl-data": [],
            "alr-data": [],
            "can_view_asl": can_view_asl,
        }

        # Process ASL data
        for prescription, prescriber in asl_prescriptions:
            asl_item = {
                "prescription_id": prescription.id,
                "DSPID": prescription.DSPID,
                "status": prescription.get_status().name.title(),
                "drug-name": prescription.drug_name,
                "drug-code": prescription.drug_code,
                "dose-instr": prescription.dose_instr,
                "dose-qty": prescription.dose_qty,
                "dose-rpt": prescription.dose_rpt,
                "prescribed-date": prescription.prescribed_date,
                "paperless": prescription.paperless,
                "brand-sub-not-prmt": prescription.brand_sub_not_prmt,
                "prescriber": {
                    "fname": prescriber.fname,
                    "lname": prescriber.lname,
                    "title": prescriber.title,
                    "address-1": prescriber.address_1,
                    "address-2": prescriber.address_2,
                    "id": prescriber.prescriber_id,
                    "hpii": prescriber.hpii,
                    "hpio": prescriber.hpio,
                    "phone": prescriber.phone,
                    "fax": prescriber.fax,
                },
            }
            pt_data["asl-data"].append(asl_item)

        # Process ALR data
        for prescription, prescriber in alr_prescriptions:
            alr_item = {
                "prescription_id": prescription.id,
                "DSPID": prescription.DSPID,
                "drug-name": prescription.drug_name,
                "drug-code": prescription.drug_code,
                "dose-instr": prescription.dose_instr,
                "dose-qty": prescription.dose_qty,
                "dose-rpt": prescription.dose_rpt,
                "prescribed-date": prescription.prescribed_date,
                "dispensed-date": prescription.dispensed_date,
                "paperless": prescription.paperless,
                "brand-sub-not-prmt": prescription.brand_sub_not_prmt,
                "remaining-repeats": prescription.remaining_repeats,
                "prescriber": {
                    "fname": prescriber.fname,
                    "lname": prescriber.lname,
                    "title": prescriber.title,
                    "address-1": prescriber.address_1,
                    "address-2": prescriber.address_2,
                    "id": prescriber.prescriber_id,
                    "hpii": prescriber.hpii,
                    "hpio": prescriber.hpio,
                    "phone": prescriber.phone,
                    "fax": prescriber.fax,
                },
            }
            pt_data["alr-data"].append(alr_item)

        # Get ASL record data (carer information, notes, etc.)
        from .models import ASL

        asl_record = ASL.query.filter_by(patient_id=pt).first()
        pt_data["carer"] = {
            "name": asl_record.carer_name if asl_record else "",
            "relationship": asl_record.carer_relationship if asl_record else "",
            "mobile": asl_record.carer_mobile if asl_record else "",
            "email": asl_record.carer_email if asl_record else "",
        }
        pt_data["notes"] = asl_record.notes if asl_record else ""

        return render_template("views/asl.html", pt=pt, pt_data=pt_data)

    except Exception as e:
        return f"Error loading ASL data: {str(e)}", 500


# API routes with authentication
@views.route("/api/asl/<int:pt>/refresh", methods=["POST"])
@login_required
def refresh_asl(pt: int):
    """Refresh Button - check for patient replies and update PENDING prescriptions"""
    try:
        patient = Patient.query.get_or_404(pt)

        if patient.asl_status == ASLStatus.PENDING.value:
            patient.asl_status = ASLStatus.GRANTED.value
            patient.consent_last_updated = datetime.now().strftime("%d/%m/%Y %H:%M")

            updated_count = Prescription.query.filter_by(
                patient_id=pt, status=PrescriptionStatus.PENDING.value
            ).update({"status": PrescriptionStatus.AVAILABLE.value})

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": f"Patient {patient.name} replied and granted access! {updated_count} prescriptions now available.",
                    "updated_prescriptions": updated_count,
                    "should_reload": True,
                    "consent-status": {
                        "is-registered": patient.is_registered,
                        "status": patient.get_asl_status()
                        .name.replace("_", " ")
                        .title(),
                        "last-updated": patient.consent_last_updated,
                    },
                }
            )

        elif patient.asl_status == ASLStatus.GRANTED.value:
            updated_count = Prescription.query.filter_by(
                patient_id=pt, status=PrescriptionStatus.PENDING.value
            ).update({"status": PrescriptionStatus.AVAILABLE.value})

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "message": f"ASL refreshed for patient {patient.name}. {updated_count} new prescriptions found.",
                    "updated_prescriptions": updated_count,
                    "should_reload": updated_count > 0,
                }
            )

        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Cannot refresh ASL - status is {patient.get_asl_status().name.replace("_", " ").title()}',
                    }
                ),
                403,
            )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/api/asl/<int:pt>/request-access", methods=["POST"])
@login_required
def request_access(pt: int):
    """Request access Button - handle proper ASL status transitions"""
    try:
        patient = Patient.query.get_or_404(pt)
        current_status = patient.get_asl_status()

        if current_status != ASLStatus.NO_CONSENT:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f'Cannot request access - current status is {current_status.name.replace("_", " ").title()}',
                    }
                ),
                400,
            )

        patient.asl_status = ASLStatus.PENDING.value
        patient.consent_last_updated = datetime.now().strftime("%d/%m/%Y %H:%M")

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Access request sent to {patient.name}. Patient will receive SMS/email to approve.",
                "consent-status": {
                    "is-registered": patient.is_registered,
                    "status": "Pending",
                    "last-updated": patient.consent_last_updated,
                },
                "should_disable_button": True,
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/api/patient/<int:pt>/consent", methods=["DELETE"])
@login_required
def delete_consent(pt: int):
    """Delete consent - reset ASL status to NO_CONSENT for re-requesting"""
    try:
        patient = Patient.query.get_or_404(pt)

        patient.asl_status = ASLStatus.NO_CONSENT.value
        patient.consent_last_updated = datetime.now().strftime("%d/%m/%Y %H:%M")

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Consent record deleted for {patient.name}. Can now request access again.",
                "consent-status": {
                    "is-registered": patient.is_registered,
                    "status": "No Consent",
                    "last-updated": patient.consent_last_updated,
                },
                "should_reload": True,
            }
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/api/asl/<int:pt>/search")
@login_required
def search_asl(pt: int):
    """Search ASL prescriptions - only if access granted"""
    try:
        patient = Patient.query.get_or_404(pt)

        if not patient.can_view_asl():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Cannot search - no access to patient ASL",
                    }
                ),
                403,
            )

        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"success": False, "error": "Search query required"})

        results = (
            db.session.query(Prescription, Prescriber)
            .join(Prescriber, Prescription.prescriber_id == Prescriber.id)
            .filter(
                Prescription.patient_id == pt,
                or_(
                    Prescription.drug_name.ilike(f"%{query}%"),
                    Prescription.drug_code.ilike(f"%{query}%"),
                    Prescriber.fname.ilike(f"%{query}%"),
                    Prescriber.lname.ilike(f"%{query}%"),
                ),
            )
            .all()
        )

        search_results = []
        for prescription, prescriber in results:
            search_results.append(
                {
                    "prescription_id": prescription.id,
                    "drug_name": prescription.drug_name,
                    "drug_code": prescription.drug_code,
                    "prescriber_name": f"{prescriber.lname}, {prescriber.fname}",
                    "status": prescription.get_status().name.title(),
                    "prescribed_date": prescription.prescribed_date,
                }
            )

        return jsonify(
            {"success": True, "results": search_results, "count": len(search_results)}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/api/prescriptions/print-selected", methods=["POST"])
@login_required
def print_selected_prescriptions():
    """Print selected prescriptions from ASL - only if access granted"""
    try:
        prescription_ids = request.json.get("prescription_ids", [])

        if not prescription_ids:
            return jsonify({"success": False, "error": "No prescriptions selected"})

        prescriptions = Prescription.query.filter(
            Prescription.id.in_(prescription_ids)
        ).all()

        for prescription in prescriptions:
            if not prescription.patient.can_view_asl():
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Cannot print - no access to {prescription.patient.name} ASL",
                        }
                    ),
                    403,
                )

        print_data = []
        for prescription in prescriptions:
            prescriber = prescription.prescriber
            patient = prescription.patient

            print_item = {
                "medicare": patient.medicare,
                "pharmaceut-ben-entitlement-no": patient.pharmaceut_ben_entitlement_no,
                "sfty-net-entitlement-cardholder": patient.sfty_net_entitlement_cardholder,
                "rpbs-ben-entitlement-cardholder": patient.rpbs_ben_entitlement_cardholder,
                "name": patient.name,
                "dob": patient.dob,
                "preferred-contact": patient.preferred_contact,
                "address-1": patient.address or "",
                "address-2": "",  # Patient model doesn't have address_2
                "script-date": patient.script_date,
                "pbs": patient.pbs,
                "rpbs": patient.rpbs,
                "prescription_id": prescription.id,
                "DSPID": prescription.DSPID,
                "status": prescription.get_status().name.title(),
                "drug-name": prescription.drug_name,
                "drug-code": prescription.drug_code,
                "dose-instr": prescription.dose_instr,
                "dose-qty": prescription.dose_qty,
                "dose-rpt": prescription.dose_rpt,
                "prescribed-date": prescription.prescribed_date,
                "paperless": prescription.paperless,
                "brand-sub-not-prmt": prescription.brand_sub_not_prmt,
                "clinician-name-and-title": f"{prescriber.fname} {prescriber.lname}"
                + (f" {prescriber.title}" if prescriber.title else ""),
                "clinician-address-1": prescriber.address_1,
                "clinician-address-2": prescriber.address_2,
                "clinician-id": prescriber.prescriber_id,
                "hpii": prescriber.hpii,
                "hpio": prescriber.hpio,
                "clinician-phone": prescriber.phone,
                "clinician-fax": prescriber.fax,
            }
            print_data.append(print_item)

        return jsonify(
            {"success": True, "print_data": print_data, "count": len(print_data)}
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@views.route("/api/dispense/<int:patient_id>", methods=["POST"])
@login_required
def dispense_prescriptions(patient_id):
    """Handle prescription dispensing for students and teachers"""
    try:
        # Get form data
        prescription_ids = request.form.get("prescription_ids", "").split(",")
        dispensed_by = request.form.get("dispensed_by", "")
        dispensed_date = request.form.get("dispensed_date", "")
        dispensing_notes = request.form.get("dispensing_notes", "")

        if not prescription_ids or not prescription_ids[0]:
            return jsonify({"success": False, "message": "No prescriptions selected"})

        if not dispensed_by:
            return jsonify(
                {"success": False, "message": "Dispensed by field is required"}
            )

        # Convert prescription IDs to integers
        prescription_ids = [int(pid) for pid in prescription_ids if pid.strip()]

        # Get prescriptions
        prescriptions = Prescription.query.filter(
            Prescription.id.in_(prescription_ids), Prescription.patient_id == patient_id
        ).all()

        if len(prescriptions) != len(prescription_ids):
            return jsonify(
                {"success": False, "message": "Some prescriptions not found"}
            )

        # Update prescriptions to dispensed status
        dispensed_count = 0

        for prescription in prescriptions:
            # Check if already dispensed
            if prescription.status == PrescriptionStatus.DISPENSED.value:
                continue

            # Update prescription status
            prescription.status = PrescriptionStatus.DISPENSED.value
            prescription.dispensed_date = dispensed_date
            prescription.dispensed_at_this_pharmacy = True

            # Handle repeats - if this prescription has repeats, initialize remaining_repeats if not set
            if prescription.dose_rpt > 0:
                if prescription.remaining_repeats is None:
                    prescription.remaining_repeats = prescription.dose_rpt
                # Don't reduce repeats here - this happens when the prescription moves to ALR

            dispensed_count += 1

        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Successfully dispensed {dispensed_count} prescription(s)",
                "dispensed_count": dispensed_count,
            }
        )

    except ValueError as e:
        return jsonify({"success": False, "message": "Invalid prescription IDs"})
    except Exception as e:
        db.session.rollback()
        return jsonify(
            {"success": False, "message": f"Error dispensing prescriptions: {str(e)}"}
        )


@views.route("/prescription")
@login_required
def prescription():
    """Printing pdf - requires login"""
    return render_template("views/prescription/prescription.html")


@views.route("/patient/<int:patient_id>/asl", methods=["GET", "POST"])
def patient_asl_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Load or create ASL record for this patient
    asl = ASL.query.filter_by(patient_id=patient.id).first()
    if not asl:
        asl = ASL(patient_id=patient.id)

    form = ASLForm(obj=asl)

    # Pre-populate form with patient data on GET request
    if request.method == "GET":
        # Pre-fill with existing patient preferred_contact if available
        if patient.preferred_contact:
            form.preferred_contact.data = patient.preferred_contact

        # Set default consent status to current patient ASL status if not already set
        if not asl.consent_status and hasattr(patient, "asl_status"):
            form.consent_status.data = str(patient.asl_status)
        elif asl.consent_status:
            form.consent_status.data = str(asl.consent_status)

    if form.validate_on_submit():
        # Save ASL-specific fields
        asl.carer_name = form.carer_name.data
        asl.carer_relationship = form.carer_relationship.data
        asl.carer_mobile = form.carer_mobile.data
        asl.carer_email = form.carer_email.data
        asl.notes = form.notes.data
        asl.consent_status = int(form.consent_status.data)

        # Update patient’s preferred contact (lives in Patient model)
        patient.preferred_contact = form.preferred_contact.data

        # Set patient as registered when the form is submitted
        patient.is_registered = True

        # Set ASL status to PENDING when registering
        asl.consent_status = ASLStatus.PENDING.value
        patient.asl_status = ASLStatus.PENDING.value

        db.session.add(asl)
        db.session.commit()

        flash(f"ASL record saved for {patient.given_name or patient.name}!", "success")

        # Redirect to ASL view to show the saved data
        return redirect(url_for("views.asl", pt=patient.id))

    return render_template(
        "views/aslregister.html",
        form=form,
        patient=patient,
    )


@views.route("/ac")  # Maybe '/api/ac'
def ac():
    text = request.args.get("text")
    if not text:
        return jsonify({"error": "Missing required parameter: text"}), 400

    api_key = "704bfce1792e462e9c9f537ffbc6cc6d"
    url = "https://api.geoapify.com/v1/geocode/autocomplete"

    # Call Geoapify
    params = {
        "text": text,
        "apiKey": api_key,
        "lang": "en",
        "limit": 5,
        "filter": "countrycode:au",
        "format": "json",
    }

    resp = requests.get(url, params=params)

    return resp.json()["results"]


@views.route("/assign")
@login_required
def assign_dashboard():
    scenario_id = request.args.get("scenario_id")
    scenario = None

    if scenario_id:
        scenario = Scenario.query.get_or_404(int(scenario_id))
        # Check if user has permission to view this scenario
        if current_user.is_teacher() and scenario.teacher_id != current_user.id:
            flash("You can only assign students to scenarios you created.", "error")
            return redirect(url_for("views.teacher_dashboard"))

    # Get all students for assignment
    all_students = User.query.filter_by(role="student").all()

    # Filter out students already assigned to this scenario
    unassigned_students = all_students
    if scenario:
        # Get currently assigned student IDs for this scenario
        assigned_student_ids = [
            s.id
            for s in User.query.join(StudentScenario)
            .filter(StudentScenario.scenario_id == scenario.id)
            .all()
        ]
        # Filter out already assigned students
        unassigned_students = [
            s for s in all_students if s.id not in assigned_student_ids
        ]

    # Get all patients excluding the active patient for this scenario
    available_patients = Patient.query.all()
    if scenario and scenario.active_patient_id:
        available_patients = [
            p for p in available_patients if p.id != scenario.active_patient_id
        ]

    return render_template(
        "views/assign.html",
        scenario=scenario,
        students=unassigned_students,
        available_patients=available_patients,
    )


@views.route("/scenarios/<int:scenario_id>/assign-students", methods=["POST"])
@teacher_required
def assign_students_to_scenario(scenario_id):
    """Assign students to scenario via AJAX"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        return jsonify(
            {
                "success": False,
                "message": "You can only assign students to scenarios you created.",
            }
        )

    form = EmptyForm()
    if form.validate_on_submit():
        try:
            assignments_data = []
            # Parse the assignments from form data
            index = 0
            while f"assignments[{index}][student_id]" in request.form:
                student_id = request.form[f"assignments[{index}][student_id]"]
                patient_id = request.form[f"assignments[{index}][patient_id]"]
                assignments_data.append(
                    {"student_id": int(student_id), "patient_id": int(patient_id)}
                )
                index += 1

            if not assignments_data:
                return jsonify(
                    {"success": False, "message": "No assignments provided."}
                )

            # Create the assignments
            assignments_created = 0
            for assignment_data in assignments_data:
                # Check if student is already assigned to this scenario
                existing = StudentScenario.query.filter_by(
                    scenario_id=scenario_id, student_id=assignment_data["student_id"]
                ).first()

                if not existing:
                    assignment = StudentScenario(
                        scenario_id=scenario_id,
                        student_id=assignment_data["student_id"],
                    )
                    db.session.add(assignment)
                    assignments_created += 1

            db.session.commit()

            return jsonify(
                {
                    "success": True,
                    "count": assignments_created,
                    "message": f"Successfully assigned {assignments_created} students to {scenario.name}!",
                }
            )

        except Exception as e:
            db.session.rollback()
            return jsonify(
                {"success": False, "message": "Error creating student assignments."}
            )

    return jsonify({"success": False, "message": "Invalid form submission."})


@views.route("/scenarios/<int:scenario_id>/unassign/<int:student_id>", methods=["POST"])
@teacher_required
def unassign_student_from_scenario(scenario_id, student_id):
    """Remove a single student from a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)
    student = User.query.get_or_404(student_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only unassign students from scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        assignment = StudentScenario.query.filter_by(
            scenario_id=scenario_id, student_id=student_id
        ).first()

        if assignment:
            try:
                db.session.delete(assignment)
                db.session.commit()
                flash(
                    f"Successfully removed {student.first_name} {student.last_name} from {scenario.name}.",
                    "success",
                )
            except Exception as e:
                db.session.rollback()
                flash("Error removing student from scenario.", "error")
        else:
            flash(
                f"{student.first_name} {student.last_name} is not assigned to this scenario.",
                "warning",
            )

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/<int:scenario_id>/unassign-all", methods=["POST"])
@teacher_required
def unassign_all_students(scenario_id):
    """Remove all students from a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only unassign students from scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        try:
            assignments = StudentScenario.query.filter_by(scenario_id=scenario_id).all()
            student_count = len(assignments)

            for assignment in assignments:
                db.session.delete(assignment)

            db.session.commit()

            if student_count > 0:
                flash(
                    f"Successfully removed all {student_count} students from {scenario.name}.",
                    "success",
                )
            else:
                flash("No students were assigned to this scenario.", "info")

        except Exception as e:
            db.session.rollback()
            flash("Error removing students from scenario.", "error")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/patients", methods=["GET"])
@teacher_required
def patient_dashboard():
    patients = Patient.query.all()
    delete_form = DeleteForm()  # one form instance reused

    # Calculate ASL statistics
    asl_granted_count = sum(1 for patient in patients if patient.can_view_asl())
    asl_pending_count = sum(
        1 for patient in patients if patient.asl_status == ASLStatus.PENDING.value
    )
    asl_rejected_count = sum(
        1 for patient in patients if patient.asl_status == ASLStatus.REJECTED.value
    )
    no_consent_count = sum(
        1 for patient in patients if patient.asl_status == ASLStatus.NO_CONSENT.value
    )

    return render_template(
        "views/patient_dash.html",
        patients=patients,
        delete_form=delete_form,
        asl_granted_count=asl_granted_count,
        asl_pending_count=asl_pending_count,
        asl_rejected_count=asl_rejected_count,
        no_consent_count=no_consent_count,
    )


@views.route("/patients/delete/<int:patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    form = DeleteForm()
    if form.validate_on_submit():
        try:
            patient = Patient.query.get_or_404(patient_id)

            # Delete related records first to avoid foreign key constraint errors

            # 1. Delete all prescriptions for this patient
            Prescription.query.filter_by(patient_id=patient_id).delete()

            # 2. Delete ASL records for this patient
            ASL.query.filter_by(patient_id=patient_id).delete()

            # 3. Delete submissions for this patient
            Submission.query.filter_by(patient_id=patient_id).delete()

            # 4. Delete scenario patient assignments for this patient
            ScenarioPatient.query.filter_by(patient_id=patient_id).delete()

            # 5. Remove this patient as active patient from any scenarios
            scenarios_with_this_patient = Scenario.query.filter_by(
                active_patient_id=patient_id
            ).all()
            for scenario in scenarios_with_this_patient:
                scenario.active_patient_id = None

            # 6. Finally delete the patient
            db.session.delete(patient)
            db.session.commit()

            flash("Patient and all related records deleted successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting patient: {str(e)}", "error")
    else:
        flash("CSRF check failed!", "danger")

    return redirect(url_for("views.patient_dashboard"))


@views.route("/patients/bulk-delete", methods=["POST"])
@teacher_required
def bulk_delete_patients():
    """Delete multiple patients at once"""
    patient_ids = request.form.getlist("patient_ids")

    if not patient_ids:
        flash("No patients selected for deletion.", "error")
        return redirect(url_for("views.patient_dashboard"))

    try:
        # Convert to integers and validate
        patient_ids = [int(id) for id in patient_ids]

        # Get patients to verify they exist
        patients = Patient.query.filter(Patient.id.in_(patient_ids)).all()

        if len(patients) != len(patient_ids):
            flash("Some selected patients were not found.", "error")
            return redirect(url_for("views.patient_dashboard"))

        # Delete all patients and their related records
        deleted_count = 0
        for patient in patients:
            try:
                # Delete related records first to avoid foreign key constraint errors

                # 1. Delete all prescriptions for this patient
                Prescription.query.filter_by(patient_id=patient.id).delete()

                # 2. Delete ASL records for this patient
                ASL.query.filter_by(patient_id=patient.id).delete()

                # 3. Delete submissions for this patient
                Submission.query.filter_by(patient_id=patient.id).delete()

                # 4. Delete scenario patient assignments for this patient
                ScenarioPatient.query.filter_by(patient_id=patient.id).delete()

                # 5. Remove this patient as active patient from any scenarios
                scenarios_with_this_patient = Scenario.query.filter_by(
                    active_patient_id=patient.id
                ).all()
                for scenario in scenarios_with_this_patient:
                    scenario.active_patient_id = None

                # 6. Finally delete the patient
                db.session.delete(patient)
                deleted_count += 1

            except Exception as e:
                flash(
                    f"Error deleting patient {patient.name or 'Unnamed'}: {str(e)}",
                    "error",
                )
                continue

        db.session.commit()
        flash(
            f"Successfully deleted {deleted_count} patient(s) and all related records.",
            "success",
        )

    except ValueError:
        flash("Invalid patient IDs provided.", "error")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting patients. Please try again.", "error")

    return redirect(url_for("views.patient_dashboard"))


@views.route("/scenarios/<int:scenario_id>/name", methods=["POST"])
@teacher_required
def update_scenario_name(scenario_id):
    """Update the name of a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        scenario_name = request.form.get("scenario_name", "").strip()
        if scenario_name:
            scenario.name = scenario_name

            try:
                db.session.commit()
                flash("Scenario name updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error updating scenario name.", "error")
        else:
            flash("Scenario name cannot be empty.", "error")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/<int:scenario_id>/question", methods=["POST"])
@teacher_required
def update_scenario_question(scenario_id):
    """Update the question text for a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        question_text = request.form.get("question_text", "").strip()
        scenario.question_text = question_text if question_text else None

        try:
            db.session.commit()
            flash("Scenario questions updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating scenario questions.", "error")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/<int:scenario_id>/description", methods=["POST"])
@teacher_required
def update_scenario_description(scenario_id):
    """Update the description for a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        description = request.form.get("description", "").strip()
        scenario.description = description if description else None

        try:
            db.session.commit()
            flash("Scenario description updated successfully!", "success")
        except Exception as e:
            db.session.rollback()
            flash("Error updating scenario description.", "error")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/<int:scenario_id>/set-patient", methods=["POST"])
@teacher_required
def set_active_patient(scenario_id):
    """Set the active patient for a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        patient_id = request.form.get("patient_id")
        if patient_id:
            patient = Patient.query.get_or_404(int(patient_id))
            scenario.active_patient_id = patient.id

            try:
                db.session.commit()
                flash(
                    f"Successfully set {patient.first_name} {patient.last_name} as the active patient for this scenario.",
                    "success",
                )
            except Exception as e:
                db.session.rollback()
                flash("Error setting active patient.", "error")
        else:
            flash("Please select a patient.", "error")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/<int:scenario_id>/remove-patient", methods=["POST"])
@teacher_required
def remove_active_patient(scenario_id):
    """Remove the active patient from a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only edit scenarios you created.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    form = EmptyForm()
    if form.validate_on_submit():
        if scenario.active_patient:
            patient_name = f"{scenario.active_patient.first_name} {scenario.active_patient.last_name}"
            scenario.active_patient_id = None

            try:
                db.session.commit()
                flash(
                    f"Successfully removed {patient_name} as the active patient.",
                    "success",
                )
            except Exception as e:
                db.session.rollback()
                flash("Error removing active patient.", "error")
        else:
            flash("No active patient to remove.", "warning")

    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))


@views.route("/scenarios/create", methods=["POST"])
@teacher_required
def create_scenario():
    """Create a new blank scenario and redirect back to dashboard"""
    form = EmptyForm()
    if form.validate_on_submit():
        new_scenario = Scenario(
            name=f"Scenario {Scenario.query.count() + 1}",  # auto-number
            description="Basic ASL workflow practice",
            teacher_id=current_user.id,
            version=1,
        )
        db.session.add(new_scenario)
        db.session.commit()
        flash("New scenario created!", "success")
    else:
        flash("Invalid CSRF token. Please try again.", "error")

    return redirect(url_for("views.teacher_dashboard"))


@views.route("/scenarios/bulk-delete", methods=["POST"])
@teacher_required
def bulk_delete_scenarios():
    """Delete multiple scenarios at once"""
    scenario_ids = request.form.getlist("scenario_ids")

    if not scenario_ids:
        flash("No scenarios selected for deletion.", "error")
        return redirect(url_for("views.teacher_dashboard"))

    try:
        # Convert to integers and validate
        scenario_ids = [int(id) for id in scenario_ids]

        # Get scenarios and verify ownership
        scenarios = Scenario.query.filter(
            Scenario.id.in_(scenario_ids), Scenario.teacher_id == current_user.id
        ).all()

        if len(scenarios) != len(scenario_ids):
            flash(
                "Some scenarios could not be found or you don't have permission to delete them.",
                "error",
            )
            return redirect(url_for("views.teacher_dashboard"))

        # Delete all scenarios
        deleted_count = 0
        for scenario in scenarios:
            db.session.delete(scenario)
            deleted_count += 1

        db.session.commit()
        flash(f"Successfully deleted {deleted_count} scenario(s).", "success")

    except ValueError:
        flash("Invalid scenario IDs provided.", "error")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting scenarios. Please try again.", "error")

    return redirect(url_for("views.teacher_dashboard"))


@views.route("/asl/ingest", methods=["POST"])
def asl_ingest():
    pt_data = request.get_json(force=True)
    # print("DEBUG pt_data:", pt_data)
    try:
        pt_data = request.get_json(force=True)
        result = ingest_pt_data_contract(pt_data, db.session, commit=True)
        return (
            jsonify(
                {
                    "status": "success",
                    "patient_id": result.patient.id,
                    "created_prescriptions": result.created_prescriptions,
                    "is_new_patient": result.is_new_patient,
                }
            ),
            201,
        )
    except Exception as e:
        import traceback

        # print("Error in asl_ingest:", str(e))
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 400


@views.route("/asl/form/<int:patient_id>", methods=["GET", "POST"])
def asl_form(patient_id):
    """ASL form - pre-populate with patient data"""
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":
        # print(f"DEBUG: ASL form POST received for patient {patient_id}")
        # print(f"DEBUG: Form data keys: {list(request.form.keys())}")
        # Handle form submission
        try:
            # Extract patient data from form
            pt_data = request.form.to_dict()

            # Update patient information
            if "pt_data[name]" in pt_data and pt_data["pt_data[name]"]:
                # Split full name into first and last name
                full_name = pt_data["pt_data[name]"].strip()
                name_parts = full_name.split(" ", 1)
                patient.given_name = name_parts[0] if name_parts else ""
                patient.last_name = name_parts[1] if len(name_parts) > 1 else ""
                patient.name = full_name

            # Update other patient fields
            if "pt_data[medicare]" in pt_data:
                patient.medicare = pt_data["pt_data[medicare]"]

            if "pt_data[pharmaceut-ben-entitlement-no]" in pt_data:
                patient.pharmaceut_ben_entitlement_no = pt_data[
                    "pt_data[pharmaceut-ben-entitlement-no]"
                ]

            if "pt_data[preferred-contact]" in pt_data:
                patient.preferred_contact = pt_data["pt_data[preferred-contact]"]

            if "pt_data[dob]" in pt_data:
                patient.dob = pt_data["pt_data[dob]"]

            if "pt_data[script-date]" in pt_data:
                patient.script_date = pt_data["pt_data[script-date]"]

            if "pt_data[address-1]" in pt_data:
                patient.address = pt_data["pt_data[address-1]"]

            # Parse address line 2 (suburb state postcode)
            if "pt_data[address-2]" in pt_data and pt_data["pt_data[address-2]"]:
                address_parts = pt_data["pt_data[address-2]"].strip().split()
                if len(address_parts) >= 3:
                    patient.postcode = address_parts[-1]  # Last part is postcode
                    patient.state = address_parts[-2]  # Second to last is state
                    patient.suburb = " ".join(
                        address_parts[:-2]
                    )  # Everything else is suburb
                elif len(address_parts) == 2:
                    patient.state = address_parts[0]
                    patient.postcode = address_parts[1]
                elif len(address_parts) == 1:
                    patient.suburb = address_parts[0]

            # Update entitlement flags
            if "pt_data[sfty-net-entitlement-cardholder]" in pt_data:
                patient.sfty_net_entitlement_cardholder = (
                    pt_data["pt_data[sfty-net-entitlement-cardholder]"].lower()
                    == "true"
                )

            if "pt_data[rpbs-ben-entitlement-cardholder]" in pt_data:
                patient.rpbs_ben_entitlement_cardholder = (
                    pt_data["pt_data[rpbs-ben-entitlement-cardholder]"].lower()
                    == "true"
                )

            # Update additional fields
            if "pt_data[pbs]" in pt_data:
                patient.pbs = (
                    pt_data["pt_data[pbs]"] if pt_data["pt_data[pbs]"] else None
                )

            if "pt_data[rpbs]" in pt_data:
                patient.rpbs = (
                    pt_data["pt_data[rpbs]"] if pt_data["pt_data[rpbs]"] else None
                )

            # Update consent status information
            if "pt_data[consent-status][is-registered]" in pt_data:
                patient.is_registered = (
                    pt_data["pt_data[consent-status][is-registered]"].lower() == "true"
                )

            if "pt_data[consent-status][status]" in pt_data:
                # Map consent status to ASL status
                status_value = pt_data["pt_data[consent-status][status]"]
                if status_value == "Granted":
                    patient.asl_status = ASLStatus.GRANTED.value
                elif status_value == "Pending":
                    patient.asl_status = ASLStatus.PENDING.value
                else:
                    patient.asl_status = ASLStatus.NO_CONSENT.value

            if "pt_data[consent-status][last-updated]" in pt_data:
                patient.consent_last_updated = (
                    pt_data["pt_data[consent-status][last-updated]"]
                    if pt_data["pt_data[consent-status][last-updated]"]
                    else None
                )

            # Set patient as registered (fallback)
            if not hasattr(patient, "is_registered") or patient.is_registered is None:
                patient.is_registered = True

            # Process prescription data (ASL and ALR items)
            from .models import ASL, Prescription, Prescriber

            # Save ASL data to ASL table
            # Check if ASL record exists for this patient
            asl_record = ASL.query.filter_by(patient_id=patient_id).first()
            if not asl_record:
                asl_record = ASL(patient_id=patient_id)
                db.session.add(asl_record)

            # Update ASL record with form data
            asl_record.consent_status = patient.asl_status
            if "pt_data[carer][name]" in pt_data:
                asl_record.carer_name = pt_data["pt_data[carer][name]"]
            if "pt_data[carer][relationship]" in pt_data:
                asl_record.carer_relationship = pt_data["pt_data[carer][relationship]"]
            if "pt_data[carer][mobile]" in pt_data:
                asl_record.carer_mobile = pt_data["pt_data[carer][mobile]"]
            if "pt_data[carer][email]" in pt_data:
                asl_record.carer_email = pt_data["pt_data[carer][email]"]
            if "pt_data[notes]" in pt_data:
                asl_record.notes = pt_data["pt_data[notes]"]

            # Clear existing prescriptions for this patient to replace with new data
            Prescription.query.filter_by(patient_id=patient_id).delete()

            # Process ASL prescriptions (pt_data[asl-data])
            # Find all ASL prescription indices
            asl_indices = set()
            for key in pt_data.keys():
                if "pt_data[asl-data]" in key and "[prescription_id]" in key:
                    # Extract index from key like pt_data[asl-data][0][prescription_id]
                    start = key.find("[asl-data][") + len("[asl-data][")
                    end = key.find("]", start)
                    if start < end:
                        try:
                            asl_indices.add(int(key[start:end]))
                        except ValueError:
                            continue

            # Process each ASL prescription
            for idx in asl_indices:
                # Get prescription data
                prescription_id = pt_data.get(
                    f"pt_data[asl-data][{idx}][prescription_id]"
                )
                if not prescription_id:
                    continue

                # Create or get prescriber
                prescriber_fname = pt_data.get(
                    f"pt_data[asl-data][{idx}][prescriber][fname]", ""
                )
                prescriber_lname = pt_data.get(
                    f"pt_data[asl-data][{idx}][prescriber][lname]", ""
                )
                prescriber_id_num = pt_data.get(
                    f"pt_data[asl-data][{idx}][prescriber][id]", ""
                )

                if prescriber_fname and prescriber_lname:
                    prescriber = Prescriber(
                        fname=prescriber_fname,
                        lname=prescriber_lname,
                        title=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescriber][title]", ""
                        ),
                        address_1=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescriber][address-1]", ""
                        ),
                        address_2=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescriber][address-2]", ""
                        ),
                        prescriber_id=(
                            int(prescriber_id_num) if prescriber_id_num else None
                        ),
                        hpii=int(
                            pt_data.get(
                                f"pt_data[asl-data][{idx}][prescriber][hpii]", "0"
                            )
                            or 0
                        ),
                        hpio=int(
                            pt_data.get(
                                f"pt_data[asl-data][{idx}][prescriber][hpio]", "0"
                            )
                            or 0
                        ),
                        phone=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescriber][phone]", ""
                        ),
                        fax=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescriber][fax]", ""
                        ),
                    )
                    db.session.add(prescriber)
                    db.session.flush()  # Get the prescriber ID

                    # Create prescription
                    prescription = Prescription(
                        patient_id=patient_id,
                        prescriber_id=prescriber.id,
                        DSPID=pt_data.get(f"pt_data[asl-data][{idx}][DSPID]", ""),
                        status=1,  # Available status
                        drug_name=pt_data.get(
                            f"pt_data[asl-data][{idx}][drug-name]", ""
                        ),
                        drug_code=pt_data.get(
                            f"pt_data[asl-data][{idx}][drug-code]", ""
                        ),
                        dose_instr=pt_data.get(
                            f"pt_data[asl-data][{idx}][dose-instr]", ""
                        ),
                        dose_qty=int(
                            pt_data.get(f"pt_data[asl-data][{idx}][dose-qty]", "0") or 0
                        ),
                        prescribed_date=pt_data.get(
                            f"pt_data[asl-data][{idx}][prescribed-date]", ""
                        ),
                        paperless=True,
                        dispensed_at_this_pharmacy=False,
                    )
                    db.session.add(prescription)

            # Process ALR prescriptions (pt_data[alr-data])
            alr_indices = set()
            for key in pt_data.keys():
                if "pt_data[alr-data]" in key and "[prescription_id]" in key:
                    # Extract index from key like pt_data[alr-data][0][prescription_id]
                    start = key.find("[alr-data][") + len("[alr-data][")
                    end = key.find("]", start)
                    if start < end:
                        try:
                            alr_indices.add(int(key[start:end]))
                        except ValueError:
                            continue

            # Process each ALR prescription
            for idx in alr_indices:
                # Get prescription data
                prescription_id = pt_data.get(
                    f"pt_data[alr-data][{idx}][prescription_id]"
                )
                if not prescription_id:
                    continue

                # For ALR, we'll use a default prescriber or create a minimal one
                # Since ALR prescriptions might not have complete prescriber data
                prescriber = Prescriber(
                    fname="ALR",
                    lname="Prescriber",
                    title="",
                    address_1="",
                    address_2="",
                    prescriber_id=0,
                    hpii=0,
                    hpio=0,
                    phone="",
                    fax="",
                )
                db.session.add(prescriber)
                db.session.flush()  # Get the prescriber ID

                # Create ALR prescription
                prescription = Prescription(
                    patient_id=patient_id,
                    prescriber_id=prescriber.id,
                    DSPID=pt_data.get(f"pt_data[alr-data][{idx}][DSPID]", ""),
                    status=1,  # Available status
                    drug_name=pt_data.get(f"pt_data[alr-data][{idx}][drug-name]", ""),
                    drug_code=pt_data.get(f"pt_data[alr-data][{idx}][drug-code]", ""),
                    dose_instr=pt_data.get(f"pt_data[alr-data][{idx}][dose-instr]", ""),
                    dose_qty=int(
                        pt_data.get(f"pt_data[alr-data][{idx}][dose-qty]", "0") or 0
                    ),
                    dose_rpt=int(
                        pt_data.get(f"pt_data[alr-data][{idx}][dose-rpt]", "0") or 0
                    ),
                    remaining_repeats=int(
                        pt_data.get(f"pt_data[alr-data][{idx}][remaining-repeats]", "0")
                        or 0
                    ),
                    prescribed_date=patient.script_date or "",
                    paperless=True,
                    dispensed_at_this_pharmacy=False,
                )
                db.session.add(prescription)

            # Save all changes to database
            db.session.commit()

            flash(
                "All ASL form data saved successfully! Patient details, prescriptions, and prescriber information have been stored.",
                "success",
            )

            # Redirect to ASL view after submission
            return redirect(url_for("views.asl", pt=patient_id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error saving form data: {str(e)}", "error")

    # GET request - pre-populate form with existing data
    from .models import ASL, Prescription, Prescriber

    # Get existing ASL record
    asl_record = ASL.query.filter_by(patient_id=patient_id).first()

    # Get existing prescriptions
    prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()

    # Prepare pre-populated data structure similar to what the form expects
    pt_data = {
        "medicare": patient.medicare or "",
        "pharmaceut-ben-entitlement-no": patient.pharmaceut_ben_entitlement_no or "",
        "sfty-net-entitlement-cardholder": (
            "true"
            if patient.sfty_net_entitlement_cardholder is True
            else ("false" if patient.sfty_net_entitlement_cardholder is False else "")
        ),
        "rpbs-ben-entitlement-cardholder": (
            "true"
            if patient.rpbs_ben_entitlement_cardholder is True
            else ("false" if patient.rpbs_ben_entitlement_cardholder is False else "")
        ),
        "can_view_asl": "true" if patient.can_view_asl() else "false",
        "name": patient.name or "",
        "dob": patient.dob or "",
        "preferred-contact": patient.preferred_contact or "",
        "address-1": patient.address or "",
        "address-2": f"{patient.suburb or ''} {patient.state or ''} {patient.postcode or ''}".strip(),
        "script-date": patient.script_date or "",
        "pbs": patient.pbs or "",
        "rpbs": patient.rpbs or "",
        "consent-status": {
            "is-registered": (
                "true"
                if patient.is_registered is True
                else ("false" if patient.is_registered is False else "")
            ),
            "status": (
                patient.get_asl_status().name.replace("_", " ").title()
                if patient.get_asl_status()
                else ""
            ),
            "last-updated": patient.consent_last_updated or "",
        },
        "carer": {
            "name": (
                asl_record.carer_name if asl_record and asl_record.carer_name else ""
            ),
            "relationship": (
                asl_record.carer_relationship
                if asl_record and asl_record.carer_relationship
                else ""
            ),
            "mobile": (
                asl_record.carer_mobile
                if asl_record and asl_record.carer_mobile
                else ""
            ),
            "email": (
                asl_record.carer_email if asl_record and asl_record.carer_email else ""
            ),
        },
        "notes": asl_record.notes if asl_record and asl_record.notes else "",
        "asl-data": [],
        "alr-data": [],
    }

    # Debug information
    # print(f"DEBUG: Patient {patient_id}")
    # print(
    #     f"  - sfty_net: {patient.sfty_net_entitlement_cardholder} -> {pt_data['sfty-net-entitlement-cardholder']}"
    # )
    # print(
    #     f"  - rpbs: {patient.rpbs_ben_entitlement_cardholder} -> {pt_data['rpbs-ben-entitlement-cardholder']}"
    # )
    # print(f"  - can_view_asl: {patient.can_view_asl()} -> {pt_data['can_view_asl']}")
    # print(
    #     f"  - is_registered: {patient.is_registered} -> {pt_data['consent-status']['is-registered']}"
    # )
    # print(
    #     f"  - asl_status: {patient.get_asl_status().name} -> {pt_data['consent-status']['status']}"
    # )
    # print(f"DEBUG: ASL record exists: {asl_record is not None}")
    # if asl_record:
    # print(f"  - carer_name: '{asl_record.carer_name}'")
    # print(f"  - carer_mobile: '{asl_record.carer_mobile}'")

    # Process existing prescriptions into ASL and ALR data
    for prescription in prescriptions:
        prescriber = prescription.prescriber

        prescription_data = {
            "prescription_id": prescription.id,
            "DSPID": prescription.DSPID or "",
            "status": prescription.get_status().name.title(),
            "drug-name": prescription.drug_name or "",
            "drug-code": prescription.drug_code or "",
            "dose-instr": prescription.dose_instr or "",
            "dose-qty": prescription.dose_qty or 0,
            "dose-rpt": prescription.dose_rpt or 0,
            "prescribed-date": prescription.prescribed_date or "",
            "paperless": "true" if prescription.paperless else "false",
            "brand-sub-not-prmt": (
                "true" if prescription.brand_sub_not_prmt else "false"
            ),
            "prescriber": {
                "fname": prescriber.fname or "",
                "lname": prescriber.lname or "",
                "title": prescriber.title or "",
                "address-1": prescriber.address_1 or "",
                "address-2": prescriber.address_2 or "",
                "id": str(prescriber.prescriber_id) if prescriber.prescriber_id else "",
                "hpii": (
                    f"{int(prescriber.hpii):016d}"
                    if prescriber.hpii and prescriber.hpii > 0
                    else "0000000000000000"
                ),
                "hpio": (
                    f"{int(prescriber.hpio):016d}"
                    if prescriber.hpio and prescriber.hpio > 0
                    else "0000000000000000"
                ),
                "phone": prescriber.phone or "",
                "fax": prescriber.fax or "",
            },
        }

        # Determine if this is ASL or ALR data
        if (
            prescriber.fname == "ALR"
            or prescription.remaining_repeats
            and prescription.remaining_repeats > 0
        ):
            # This is ALR data
            prescription_data["dispensed-date"] = prescription.dispensed_date or ""
            prescription_data["remaining-repeats"] = prescription.remaining_repeats or 0
            pt_data["alr-data"].append(prescription_data)
            # print(
            #     f"DEBUG: Added ALR prescription - HPI-I: {prescription_data['prescriber']['hpii']}, HPI-O: {prescription_data['prescriber']['hpio']}"
            # )
        else:
            # This is ASL data
            pt_data["asl-data"].append(prescription_data)
            # print(
            #     f"DEBUG: Added ASL prescription - HPI-I: {prescription_data['prescriber']['hpii']}, HPI-O: {prescription_data['prescriber']['hpio']}"
            # )

    # print(f"DEBUG: Final pt_data structure: {pt_data}")
    return render_template("views/asl_form.html", patient=patient, pt_data=pt_data)


@views.route("/help")
@login_required
def readme():
    """
    Renders README.md as a html page
    """
    role = "teacher" if current_user.is_teacher() else "student"
    html_path = (
        Path(__file__).resolve().parents[2]
        / "flaskr"
        / "website"
        / "templates"
        / "views"
        / "help"
        / f"help-{role}.html"
    )

    if not html_path.exists():
        render_readme()
    html_content = html_path.read_text(encoding="utf-8")

    return render_template("views/help/help.html", html=html_content)


# Submission and Grading System
@views.route(
    "/scenarios/<int:scenario_id>/submit/<int:patient_id>", methods=["GET", "POST"]
)
@login_required
def submit_work(scenario_id, patient_id):
    """Student submits their ASL work for grading"""
    if current_user.role != "student":
        flash("Only students can submit work.", "error")
        return redirect(url_for("views.home"))

    # Check if student is assigned to this scenario
    student_scenario = StudentScenario.query.filter_by(
        student_id=current_user.id, scenario_id=scenario_id
    ).first()

    if not student_scenario:
        flash("You are not assigned to this scenario.", "error")
        return redirect(url_for("views.student_dashboard"))

    # Check if student is assigned to this patient
    scenario_patient = ScenarioPatient.query.filter_by(
        student_id=current_user.id, scenario_id=scenario_id, patient_id=patient_id
    ).first()

    if not scenario_patient:
        flash("You are not assigned to this patient.", "error")
        return redirect(url_for("views.student_dashboard"))

    scenario = Scenario.query.get_or_404(scenario_id)
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "POST":
        # Handle file uploads
        uploaded_files = []
        if "pdf_file" in request.files:
            files = request.files.getlist("pdf_file")

            # Create uploads directory if it doesn't exist
            upload_folder = os.path.join(
                current_app.root_path, "uploads", "submissions"
            )
            os.makedirs(upload_folder, exist_ok=True)

            for file in files:
                if file and file.filename:
                    # Validate file size (10MB max)
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)

                    if file_size > 10 * 1024 * 1024:  # 10MB
                        flash(
                            f"File {file.filename} is too large. Maximum size is 10MB.",
                            "error",
                        )
                        continue

                    # Validate file type
                    allowed_extensions = {".pdf", ".doc", ".docx", ".txt"}
                    file_ext = os.path.splitext(file.filename)[1].lower()

                    if file_ext not in allowed_extensions:
                        flash(
                            f"File {file.filename} has unsupported format. Please use PDF, Word, or text files.",
                            "error",
                        )
                        continue

                    # Generate secure filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_filename = f"{current_user.id}_{scenario_id}_{patient_id}_{timestamp}_{secure_filename(file.filename)}"
                    file_path = os.path.join(upload_folder, safe_filename)

                    try:
                        file.save(file_path)
                        uploaded_files.append(
                            {
                                "original_name": file.filename,
                                "stored_name": safe_filename,
                                "file_path": file_path,
                                "file_size": file_size,
                                "upload_time": datetime.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        flash(f"Error uploading {file.filename}: {str(e)}", "error")

        # Create submission
        from .models import Submission

        # Get current ASL data for this patient
        asl_record = ASL.query.filter_by(patient_id=patient_id).first()
        prescriptions = Prescription.query.filter_by(patient_id=patient_id).all()

        # Create submission data snapshot
        submission_data = {
            "patient_data": {
                "medicare": patient.medicare,
                "name": patient.name,
                "dob": patient.dob,
                "address": patient.address,
                "phone": patient.phone,
                "asl_status": patient.asl_status,
            },
            "asl_record": {
                "carer_name": asl_record.carer_name if asl_record else "",
                "carer_relationship": (
                    asl_record.carer_relationship if asl_record else ""
                ),
                "notes": asl_record.notes if asl_record else "",
            },
            "prescriptions": [
                {
                    "drug_name": p.drug_name,
                    "drug_code": p.drug_code,
                    "dose_instr": p.dose_instr,
                    "dose_qty": p.dose_qty,
                    "status": p.status,
                }
                for p in prescriptions
            ],
            "uploaded_files": uploaded_files,
        }

        # Create or update submission
        existing_submission = Submission.query.filter_by(
            student_scenario_id=student_scenario.id, patient_id=patient_id
        ).first()

        if existing_submission:
            existing_submission.submission_data = submission_data
            existing_submission.notes = request.form.get("notes", "")
            existing_submission.submitted_at = datetime.now()
        else:
            submission = Submission(
                student_scenario_id=student_scenario.id,
                patient_id=patient_id,
                submission_data=submission_data,
                notes=request.form.get("notes", ""),
            )
            db.session.add(submission)

        # Update student scenario status
        student_scenario.submitted_at = datetime.now()
        student_scenario.status = "submitted"

        db.session.commit()
        flash("Work submitted successfully!", "success")
        return redirect(url_for("views.student_dashboard"))

    # GET request - show submission form
    return render_template(
        "views/submit_work.html",
        scenario=scenario,
        patient=patient,
        student_scenario=student_scenario,
    )


@views.route("/scenarios/<int:scenario_id>/submissions")
@teacher_required
def view_submissions(scenario_id):
    """Teacher views all submissions for a scenario"""
    scenario = Scenario.query.get_or_404(scenario_id)

    # Ensure teacher owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only view submissions for your own scenarios.", "error")
        return redirect(url_for("views.teacher_dash"))

    # Get all student scenarios with submissions
    student_scenarios = StudentScenario.query.filter_by(scenario_id=scenario_id).all()

    submissions_data = []
    for ss in student_scenarios:
        student = User.query.get(ss.student_id)
        submissions = Submission.query.filter_by(student_scenario_id=ss.id).all()

        submissions_data.append(
            {"student_scenario": ss, "student": student, "submissions": submissions}
        )

    return render_template(
        "views/scenario_submissions.html",
        scenario=scenario,
        submissions_data=submissions_data,
    )


@views.route("/submissions/<int:submission_id>/grade", methods=["GET", "POST"])
@teacher_required
def grade_submission(submission_id):
    """Teacher grades a specific submission"""
    submission = Submission.query.get_or_404(submission_id)
    student_scenario = submission.student_scenario
    scenario = student_scenario.scenario

    # Ensure teacher owns this scenario
    if scenario.teacher_id != current_user.id:
        flash("You can only grade submissions for your own scenarios.", "error")
        return redirect(url_for("views.teacher_dash"))

    if request.method == "POST":
        # Update grade and feedback
        score = request.form.get("score", type=float)
        feedback = request.form.get("feedback", "")

        if score is not None:
            student_scenario.score = score
            student_scenario.feedback = feedback
            student_scenario.completed_at = datetime.now()
            student_scenario.status = "graded"

            db.session.commit()
            flash("Submission graded successfully!", "success")
            return redirect(url_for("views.view_submissions", scenario_id=scenario.id))

    # GET request - show grading form
    student = User.query.get(student_scenario.student_id)
    patient = Patient.query.get(submission.patient_id)

    return render_template(
        "views/grade_submission.html",
        submission=submission,
        student_scenario=student_scenario,
        student=student,
        patient=patient,
        scenario=scenario,
    )


@views.route("/download_file/<filename>")
@login_required
def download_file(filename):
    """Download uploaded file (only for teachers/admins)"""
    if current_user.user_type not in ["teacher", "admin"]:
        flash("Unauthorized access.", "error")
        return redirect(url_for("views.student_dashboard"))

    try:
        # Ensure the uploads directory exists
        uploads_dir = os.path.join(current_app.instance_path, "uploads")
        file_path = os.path.join(uploads_dir, filename)

        # Verify file exists and is within uploads directory
        if (
            not os.path.exists(file_path)
            or not os.path.commonpath([uploads_dir, file_path]) == uploads_dir
        ):
            flash("File not found.", "error")
            return redirect(url_for("views.teacher_dash"))

        # Send file with appropriate headers
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        flash(f"Error downloading file: {str(e)}", "error")
        return redirect(url_for("views.teacher_dash"))
