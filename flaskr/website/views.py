from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ASLStatus, ASL, Scenario, User, StudentScenario, ScenarioPatient
from .forms import PatientForm, ASLForm, DeleteForm, EmptyForm
from sqlalchemy import or_
from datetime import datetime
from functools import wraps
import requests

views = Blueprint('views', __name__)

# Helper decorator to require teacher role
def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_teacher():
            flash('You need to be a teacher to access this page', 'error')
            return redirect(url_for('auth.home'))
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
            flash('You do not have access to this scenario', 'error')
            return redirect(url_for('views.student_dashboard'))
    elif current_user.is_teacher():
        # Teachers can only access scenarios they created
        if scenario.teacher_id != current_user.id:
            flash('You can only access scenarios you created', 'error')
            return redirect(url_for('views.teacher_dashboard'))
    
    # Get assigned students for this scenario
    assigned_students = User.query.join(StudentScenario).filter(
        StudentScenario.scenario_id == scenario_id
    ).all()
    
    # Get scenario patients if any
    scenario_patients = scenario.patient_data
    
    # Get all available patients for selection
    all_patients = Patient.query.all()
    
    return render_template(
        "views/scenario_dash.html", 
        scenario=scenario,
        assigned_students=assigned_students,
        scenario_patients=scenario_patients,
        all_patients=all_patients
    )


@views.route("/scenarios/<int:scenario_id>/edit", methods=["GET", "POST"])
@teacher_required
def edit_scenario(scenario_id):
    """Edit scenario details - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Ensure teacher can only edit their own scenarios
    if scenario.teacher_id != current_user.id:
        flash('You can only edit scenarios you created', 'error')
        return redirect(url_for('views.teacher_dashboard'))
    
    if request.method == 'POST':
        scenario.name = request.form.get('name', scenario.name)
        scenario.description = request.form.get('description', scenario.description)
        scenario.password = request.form.get('password') or None
        scenario.updated_at = datetime.now()
        
        db.session.commit()
        flash('Scenario updated successfully!', 'success')
        return redirect(url_for('views.scenario_dashboard', scenario_id=scenario.id))
    
    return render_template("views/edit_scenario.html", scenario=scenario)

@views.route("/scenarios/<int:scenario_id>/delete", methods=["POST"])
@teacher_required
def delete_scenario(scenario_id):
    """Delete a scenario - teachers only (archive instead of hard delete)"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Ensure teacher can only delete their own scenarios
    if scenario.teacher_id != current_user.id:
        flash('You can only delete scenarios you created', 'error')
        return redirect(url_for('views.teacher_dashboard'))
    
    form = DeleteForm()
    if form.validate_on_submit():
        try:
            # Archive instead of hard delete to preserve data integrity
            scenario.is_archived = True
            scenario.updated_at = datetime.now()
            
            db.session.commit()
            flash(f'Scenario "{scenario.name}" has been archived successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while archiving the scenario. Please try again.', 'error')
    else:
        flash('Invalid request. Please try again.', 'error')
    
    return redirect(url_for('views.teacher_dashboard'))


@views.route("/scenarios/<int:scenario_id>/assign", methods=["GET", "POST"])
@teacher_required
def assign_scenario(scenario_id):
    """Assign scenario to students - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Ensure teacher can only assign their own scenarios
    if scenario.teacher_id != current_user.id:
        flash('You can only assign scenarios you created', 'error')
        return redirect(url_for('views.teacher_dashboard'))
    
    if request.method == 'POST':
        student_ids = request.form.getlist('student_ids')
        
        # Clear existing assignments if requested
        if request.form.get('clear_existing'):
            # Remove all current assignments
            StudentScenario.query.filter_by(scenario_id=scenario.id).delete()
        
        # Add new assignments
        for student_id in student_ids:
            student = User.query.filter_by(id=student_id, role='student').first()
            if student:
                # Check if assignment already exists
                existing = StudentScenario.query.filter_by(
                    student_id=student_id,
                    scenario_id=scenario.id
                ).first()
                
                if not existing:
                    assignment = StudentScenario(
                        student_id=student_id,
                        scenario_id=scenario.id
                    )
                    db.session.add(assignment)
        
        db.session.commit()
        flash(f'Scenario assigned to {len(student_ids)} students!', 'success')
        return redirect(url_for('views.scenario_dashboard', scenario_id=scenario.id))
    
    # GET request - show assignment form
    students = User.query.filter_by(role='student', is_active=True).all()
    assigned_student_ids = [s.id for s in scenario.assigned_students]
    
    return render_template("views/assign_scenario.html", 
                         scenario=scenario, 
                         students=students,
                         assigned_student_ids=assigned_student_ids)


@views.route("/scenarios/<int:scenario_id>/assign-patient", methods=["GET", "POST"])
@teacher_required
def assign_patient_to_scenario(scenario_id):
    """Assign a patient to a scenario - teachers only"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Ensure teacher can only modify their own scenarios
    if scenario.teacher_id != current_user.id:
        flash('You can only modify scenarios you created', 'error')
        return redirect(url_for('views.teacher_dashboard'))
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        
        if patient_id:
            # Check if patient is already assigned
            existing = ScenarioPatient.query.filter_by(
                scenario_id=scenario.id,
                patient_id=patient_id
            ).first()
            
            if not existing:
                scenario_patient = ScenarioPatient(
                    scenario_id=scenario.id,
                    patient_id=patient_id
                )
                db.session.add(scenario_patient)
                db.session.commit()
                flash('Patient assigned to scenario successfully!', 'success')
            else:
                flash('Patient is already assigned to this scenario', 'info')
        else:
            flash('Please select a patient', 'error')
        
        return redirect(url_for('views.scenario_dashboard', scenario_id=scenario.id))
    
    # GET request - show patient selection form
    patients = Patient.query.filter_by(is_registered=True).all()
    assigned_patient_ids = [sp.patient_id for sp in scenario.patient_data]
    
    return render_template("views/assign_patient.html", 
                         scenario=scenario, 
                         patients=patients,
                         assigned_patient_ids=assigned_patient_ids)

@views.route("/scenarios/<int:scenario_id>/duplicate", methods=["POST"])
@teacher_required
def duplicate_scenario(scenario_id):
    """Duplicate a scenario - teachers only"""
    original_scenario = Scenario.query.get_or_404(scenario_id)
    
    # Ensure teacher can only duplicate their own scenarios
    if original_scenario.teacher_id != current_user.id:
        flash('You can only duplicate scenarios you created', 'error')
        return redirect(url_for('views.teacher_dashboard'))
    
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
                parent_scenario_id=original_scenario.id
            )
            
            db.session.add(new_scenario)
            db.session.flush()  # Get the ID
            
            # Copy patient data associations
            for patient_data in original_scenario.patient_data:
                new_patient_data = ScenarioPatient(
                    scenario_id=new_scenario.id,
                    patient_id=patient_data.patient_id
                )
                db.session.add(new_patient_data)
            
            db.session.commit()
            flash('Scenario duplicated successfully!', 'success')
            return redirect(url_for('views.scenario_dashboard', scenario_id=new_scenario.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error duplicating scenario. Please try again.', 'error')
    else:
        flash('Invalid request. Please try again.', 'error')
    
    return redirect(url_for('views.teacher_dashboard'))

@views.route('/')
def index():
    """Root route - redirects to appropriate dashboard"""
    if current_user.is_authenticated:
        if current_user.is_teacher():
            return redirect(url_for('views.teacher_dashboard'))
        else:
            return redirect(url_for('views.student_dashboard'))
    return redirect(url_for('auth.login'))

# Teacher Dashboard
@views.route('/teacher/dashboard')
@teacher_required
def teacher_dashboard():
    """Teacher dashboard showing all scenarios"""
    # Get teacher's scenarios
    scenarios = Scenario.query.filter_by(
        teacher_id=current_user.id,
        is_archived=False
    ).order_by(Scenario.created_at.desc()).all()
    
    # Get some stats
    total_scenarios = len(scenarios)
    total_students = User.query.filter_by(role='student').count()
    
    # Create forms
    form = EmptyForm()
    delete_form = DeleteForm()
    
    return render_template(
        "views/teacher_dash.html",
        scenarios=scenarios,
        total_scenarios=total_scenarios,
        total_students=total_students,
        form=form,
        delete_form=delete_form
    )

@views.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard showing assigned scenarios"""
    if current_user.is_teacher():
        return redirect(url_for('views.teacher_dashboard'))
    
    # Get student's assigned scenarios
    assigned_scenarios = current_user.assigned_scenarios
    
    return render_template(
        "views/student_dash.html",
        scenarios=assigned_scenarios
    )