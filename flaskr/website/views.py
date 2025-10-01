from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ASLStatus,ASL,Scenario,User, StudentScenario, ScenarioPatient
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
        "views/scenario_dashboard.html", 
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

@views.route('/patients/create', methods=["GET", "POST"])
def create_patient():
    form = PatientForm()

    if form.validate_on_submit():
        patient = Patient()

        # Basic details
        patient.last_name   = form.basic.lastName.data
        patient.given_name  = form.basic.givenName.data
        patient.title       = form.basic.title.data
        patient.sex         = form.basic.sex.data
        patient.dob         = form.basic.dob.data.strftime("%d/%m/%Y") if form.basic.dob.data else None
        patient.pt_number   = form.basic.ptNumber.data

        # Contact
        patient.address     = request.form.get("basic-address")
        patient.suburb      = form.basic.suburb.data
        patient.state       = form.basic.state.data
        patient.postcode    = form.basic.postcode.data
        patient.phone       = form.basic.phone.data
        patient.mobile      = form.basic.mobile.data
        patient.licence     = form.basic.licence.data
        patient.sms_repeats = form.basic.smsRepeats.data
        patient.sms_owing   = form.basic.smsOwing.data
        patient.email       = form.basic.email.data

        # Medicare
        patient.medicare         = form.basic.medicare.data
        patient.medicare_valid_to= form.basic.medicareValidTo.data
        patient.medicare_surname = form.basic.medicareSurname.data
        patient.medicare_given_name = form.basic.medicareGivenName.data

        # Concession
        patient.concession_number = form.basic.concessionNumber.data
        patient.concession_valid_to= form.basic.concessionValidTo.data.strftime("%d/%m/%Y") if form.basic.concessionValidTo.data else None
        patient.safety_net_number = form.basic.safetyNetNumber.data
        patient.repatriation_number = form.basic.repatriationNumber.data
        patient.repatriation_valid_to= form.basic.repatriationValidTo.data.strftime("%d/%m/%Y") if form.basic.repatriationValidTo.data else None
        patient.repatriation_type = form.basic.repatriationType.data
        patient.ndss_number = form.basic.ndssNumber.data

        # MyHR
        patient.ihi_number = form.basic.ihiNumber.data
        patient.ihi_status = form.basic.ihiStatus.data
        patient.ihi_record_status = form.basic.ihiRecordStatus.data

        # Doctor + flags
        patient.doctor       = form.basic.doctor.data
        patient.ctg_registered = form.basic.ctgRegistered.data
        patient.generics_only  = form.basic.genericsOnly.data
        patient.repeats_held   = form.basic.repeatsHeld.data
        patient.pt_deceased    = form.basic.ptDeceased.data

        db.session.add(patient)
        db.session.commit()

        flash("Patient created successfully!", "success")
        return redirect(url_for("views.patient_dashboard"))

    return render_template("views/edit_pt.html", form=form, patient=None)

@views.route('/patients/edit/<int:patient_id>', methods=["GET", "POST"])
@login_required
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
            form.basic.concessionValidTo.data = datetime.strptime(patient.concession_valid_to, "%d/%m/%Y")
        form.basic.safetyNetNumber.data = patient.safety_net_number
        form.basic.repatriationNumber.data = patient.repatriation_number
        if patient.repatriation_valid_to:
            form.basic.repatriationValidTo.data = datetime.strptime(patient.repatriation_valid_to, "%d/%m/%Y")
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
        patient.last_name   = form.basic.lastName.data
        patient.given_name  = form.basic.givenName.data
        patient.title       = form.basic.title.data
        patient.sex         = form.basic.sex.data
        patient.dob         = form.basic.dob.data.strftime("%d/%m/%Y") if form.basic.dob.data else None
        patient.pt_number   = form.basic.ptNumber.data

        patient.address     = request.form.get("basic-address")
        patient.suburb      = form.basic.suburb.data
        patient.state       = form.basic.state.data
        patient.postcode    = form.basic.postcode.data
        patient.phone       = form.basic.phone.data
        patient.mobile      = form.basic.mobile.data
        patient.licence     = form.basic.licence.data
        patient.sms_repeats = form.basic.smsRepeats.data
        patient.sms_owing   = form.basic.smsOwing.data
        patient.email       = form.basic.email.data

        patient.medicare            = form.basic.medicare.data
        patient.medicare_issue      = form.basic.medicareIssue.data
        patient.medicare_valid_to   = form.basic.medicareValidTo.data
        patient.medicare_surname    = form.basic.medicareSurname.data
        patient.medicare_given_name = form.basic.medicareGivenName.data

        patient.concession_number   = form.basic.concessionNumber.data
        patient.concession_valid_to = (
            form.basic.concessionValidTo.data.strftime("%d/%m/%Y")
            if form.basic.concessionValidTo.data else None
        )
        patient.safety_net_number   = form.basic.safetyNetNumber.data
        patient.repatriation_number = form.basic.repatriationNumber.data
        patient.repatriation_valid_to = (
            form.basic.repatriationValidTo.data.strftime("%d/%m/%Y")
            if form.basic.repatriationValidTo.data else None
        )
        patient.repatriation_type   = form.basic.repatriationType.data
        patient.ndss_number         = form.basic.ndssNumber.data

        patient.ihi_number        = form.basic.ihiNumber.data
        patient.ihi_status        = form.basic.ihiStatus.data
        patient.ihi_record_status = form.basic.ihiRecordStatus.data

        patient.doctor        = form.basic.doctor.data
        patient.ctg_registered = form.basic.ctgRegistered.data
        patient.generics_only  = form.basic.genericsOnly.data
        patient.repeats_held   = form.basic.repeatsHeld.data
        patient.pt_deceased    = form.basic.ptDeceased.data

        db.session.commit()
        flash("Patient updated successfully!", "success")
        return redirect(url_for("views.patient_dashboard"))

    return render_template("views/edit_pt.html", form=form, patient=patient)
    

@views.route('/show-users')
def show_users():
    from .models import User
    users = User.query.all()
    return '<br>'.join([
        f'ID: {u.id} | Username: {u.username} | Email: {u.email} | Password: {u.password} | Role: {u.role}'
        for u in users
    ])
  
@views.route('/asl/<int:pt>') 
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
            # Only get AVAILABLE prescriptions for ASL table
            asl_prescriptions = db.session.query(Prescription, Prescriber).join(
                Prescriber, Prescription.prescriber_id == Prescriber.id
            ).filter(
                Prescription.patient_id == pt,
                Prescription.status == PrescriptionStatus.AVAILABLE.value
            ).all()
            
            # get ALR prescriptions with remaining repeat
            alr_prescriptions = db.session.query(Prescription, Prescriber).join(
                Prescriber, Prescription.prescriber_id == Prescriber.id
            ).filter(
                Prescription.patient_id == pt,
                Prescription.status == PrescriptionStatus.DISPENSED.value,
                Prescription.dispensed_at_this_pharmacy == True,
                Prescription.remaining_repeats > 0
            ).all()
        
        pt_data = {
            "medicare": patient.medicare,  
            "pharmaceut-ben-entitlement-no": patient.pharmaceut_ben_entitlement_no,
            "sfty-net-entitlement-cardholder": patient.sfty_net_entitlement_cardholder,
            "rpbs-ben-entitlement-cardholder": patient.rpbs_ben_entitlement_cardholder,
            "name": patient.name,
            "dob": patient.dob,
            "preferred-contact": patient.preferred_contact,
            "address-1": patient.address_1,
            "address-2": patient.address_2,
            "script-date": patient.script_date,
            "pbs": patient.pbs,
            "rpbs": patient.rpbs,
            
            "consent-status": {
                "is-registered": patient.is_registered,
                "status": patient.get_asl_status().name.replace('_', ' ').title(),
                "last-updated": patient.consent_last_updated if patient.consent_last_updated else "01/Jan/2000 02:59AM"
            },
            
            "asl-data": [],
            "alr-data": [],
            "can_view_asl": can_view_asl
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
                }
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
                }
            }
            pt_data["alr-data"].append(alr_item)
        
        return render_template("views/asl.html", pt=pt, pt_data=pt_data)
        
    except Exception as e:
        return f"Error loading ASL data: {str(e)}", 500

# API routes with authentication
@views.route('/api/asl/<int:pt>/refresh', methods=['POST'])
@login_required
def refresh_asl(pt: int):
    """Refresh Button - check for patient replies and update PENDING prescriptions"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        if patient.asl_status == ASLStatus.PENDING.value:
            patient.asl_status = ASLStatus.GRANTED.value
            patient.consent_last_updated = datetime.now().strftime('%d/%m/%Y %H:%M')
            
            updated_count = Prescription.query.filter_by(
                patient_id=pt,
                status=PrescriptionStatus.PENDING.value
            ).update({'status': PrescriptionStatus.AVAILABLE.value})
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Patient {patient.name} replied and granted access! {updated_count} prescriptions now available.',
                'updated_prescriptions': updated_count,
                'should_reload': True,
                'consent-status': {
                    'is-registered': patient.is_registered,
                    'status': patient.get_asl_status().name.replace('_', ' ').title(),
                    'last-updated': patient.consent_last_updated
                }
            })
            
        elif patient.asl_status == ASLStatus.GRANTED.value:
            updated_count = Prescription.query.filter_by(
                patient_id=pt,
                status=PrescriptionStatus.PENDING.value
            ).update({'status': PrescriptionStatus.AVAILABLE.value})
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'ASL refreshed for patient {patient.name}. {updated_count} new prescriptions found.',
                'updated_prescriptions': updated_count,
                'should_reload': updated_count > 0
            })
            
        else:
            return jsonify({
                'success': False,
                'error': f'Cannot refresh ASL - status is {patient.get_asl_status().name.replace("_", " ").title()}'
            }), 403
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/asl/<int:pt>/request-access', methods=['POST'])
@login_required
def request_access(pt: int):
    """Request access Button - handle proper ASL status transitions"""
    try:
        patient = Patient.query.get_or_404(pt)
        current_status = patient.get_asl_status()
        
        if current_status != ASLStatus.NO_CONSENT:
            return jsonify({
                'success': False,
                'error': f'Cannot request access - current status is {current_status.name.replace("_", " ").title()}'
            }), 400
        
        patient.asl_status = ASLStatus.PENDING.value
        patient.consent_last_updated = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Access request sent to {patient.name}. Patient will receive SMS/email to approve.',
            'consent-status': {
                'is-registered': patient.is_registered,
                'status': 'Pending',
                'last-updated': patient.consent_last_updated
            },
            'should_disable_button': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/patient/<int:pt>/consent', methods=['DELETE'])
@login_required
def delete_consent(pt: int):
    """Delete consent - reset ASL status to NO_CONSENT for re-requesting"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        patient.asl_status = ASLStatus.NO_CONSENT.value
        patient.consent_last_updated = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Consent record deleted for {patient.name}. Can now request access again.',
            'consent-status': {
                'is-registered': patient.is_registered,
                'status': 'No Consent',
                'last-updated': patient.consent_last_updated
            },
            'should_reload': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/asl/<int:pt>/search')
@login_required
def search_asl(pt: int):
    """Search ASL prescriptions - only if access granted"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        if not patient.can_view_asl():
            return jsonify({
                'success': False,
                'error': 'Cannot search - no access to patient ASL'
            }), 403
            
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': False, 'error': 'Search query required'})
        
        results = db.session.query(Prescription, Prescriber).join(
            Prescriber, Prescription.prescriber_id == Prescriber.id
        ).filter(
            Prescription.patient_id == pt,
            or_(
                Prescription.drug_name.ilike(f'%{query}%'),
                Prescription.drug_code.ilike(f'%{query}%'),
                Prescriber.fname.ilike(f'%{query}%'),
                Prescriber.lname.ilike(f'%{query}%')
            )
        ).all()
        
        search_results = []
        for prescription, prescriber in results:
            search_results.append({
                'prescription_id': prescription.id,
                'drug_name': prescription.drug_name,
                'drug_code': prescription.drug_code,
                'prescriber_name': f"{prescriber.lname}, {prescriber.fname}",
                'status': prescription.get_status().name.title(),
                'prescribed_date': prescription.prescribed_date
            })
        
        return jsonify({
            'success': True,
            'results': search_results,
            'count': len(search_results)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/prescriptions/print-selected', methods=['POST'])
@login_required
def print_selected_prescriptions():
    """Print selected prescriptions from ASL - only if access granted"""
    try:
        prescription_ids = request.json.get('prescription_ids', [])
        
        if not prescription_ids:
            return jsonify({'success': False, 'error': 'No prescriptions selected'})
        
        prescriptions = Prescription.query.filter(
            Prescription.id.in_(prescription_ids)
        ).all()
        
        for prescription in prescriptions:
            if not prescription.patient.can_view_asl():
                return jsonify({
                    'success': False,
                    'error': f'Cannot print - no access to {prescription.patient.name} ASL'
                }), 403
        
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
                "address-1": patient.address_1,
                "address-2": patient.address_2,
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
                
                "clinician-name-and-title": f"{prescriber.fname} {prescriber.lname}" + (f" {prescriber.title}" if prescriber.title else ""),
                "clinician-address-1": prescriber.address_1,
                "clinician-address-2": prescriber.address_2,
                "clinician-id": prescriber.prescriber_id,
                "hpii": prescriber.hpii,
                "hpio": prescriber.hpio,
                "clinician-phone": prescriber.phone,
                "clinician-fax": prescriber.fax,
            }
            print_data.append(print_item)
        
        return jsonify({
            'success': True,
            'print_data': print_data,
            'count': len(print_data)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@views.route('/prescription')
@login_required
def prescription():
    """Printing pdf - requires login"""
    return render_template("views/prescription/prescription.html")

@views.route('/patient/<int:patient_id>/asl', methods=["GET", "POST"])
def patient_asl_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)

    # Load or create ASL record for this patient
    asl = ASL.query.filter_by(patient_id=patient.id).first()
    if not asl:
        asl = ASL(patient_id=patient.id)

    form = ASLForm(obj=asl)

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

        db.session.add(asl)
        db.session.commit()

        flash(f"ASL record saved for {patient.given_name or patient.name}!", "success")

    return render_template(
        "views/patientasl.html",
        form=form,
        patient=patient,
    )




@views.route('/ac') # Maybe '/api/ac'
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
        "format": "json"
    }

    resp = requests.get(url, params=params)

    return resp.json()['results']

@views.route("/assign")
@login_required
def assign_dashboard():
    scenario_id = request.args.get('scenario_id')
    scenario = None
    
    if scenario_id:
        scenario = Scenario.query.get_or_404(int(scenario_id))
        # Check if user has permission to view this scenario
        if current_user.is_teacher() and scenario.teacher_id != current_user.id:
            flash("You can only assign students to scenarios you created.", "error")
            return redirect(url_for("views.teacher_dashboard"))
    
    # Get all students for assignment
    all_students = User.query.filter_by(role='student').all()
    
    # Filter out students already assigned to this scenario
    unassigned_students = all_students
    if scenario:
        # Get currently assigned student IDs for this scenario
        assigned_student_ids = [s.id for s in User.query.join(StudentScenario).filter(
            StudentScenario.scenario_id == scenario.id
        ).all()]
        # Filter out already assigned students
        unassigned_students = [s for s in all_students if s.id not in assigned_student_ids]
    
    # Get all patients excluding the active patient for this scenario
    available_patients = Patient.query.all()
    if scenario and scenario.active_patient_id:
        available_patients = [p for p in available_patients if p.id != scenario.active_patient_id]
    
    return render_template("views/assign.html", scenario=scenario, students=unassigned_students, available_patients=available_patients)

@views.route("/scenarios/<int:scenario_id>/assign-students", methods=["POST"])
@teacher_required
def assign_students_to_scenario(scenario_id):
    """Assign students to scenario via AJAX"""
    scenario = Scenario.query.get_or_404(scenario_id)
    
    # Check if user owns this scenario
    if scenario.teacher_id != current_user.id:
        return jsonify({'success': False, 'message': 'You can only assign students to scenarios you created.'})
    
    form = EmptyForm()
    if form.validate_on_submit():
        try:
            assignments_data = []
            # Parse the assignments from form data
            index = 0
            while f'assignments[{index}][student_id]' in request.form:
                student_id = request.form[f'assignments[{index}][student_id]']
                patient_id = request.form[f'assignments[{index}][patient_id]']
                assignments_data.append({
                    'student_id': int(student_id),
                    'patient_id': int(patient_id)
                })
                index += 1
            
            if not assignments_data:
                return jsonify({'success': False, 'message': 'No assignments provided.'})
            
            # Create the assignments
            assignments_created = 0
            for assignment_data in assignments_data:
                # Check if student is already assigned to this scenario
                existing = StudentScenario.query.filter_by(
                    scenario_id=scenario_id,
                    student_id=assignment_data['student_id']
                ).first()
                
                if not existing:
                    assignment = StudentScenario(
                        scenario_id=scenario_id,
                        student_id=assignment_data['student_id']
                    )
                    db.session.add(assignment)
                    assignments_created += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'count': assignments_created,
                'message': f'Successfully assigned {assignments_created} students to {scenario.name}!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Error creating student assignments.'})
    
    return jsonify({'success': False, 'message': 'Invalid form submission.'})

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
            scenario_id=scenario_id,
            student_id=student_id
        ).first()
        
        if assignment:
            try:
                db.session.delete(assignment)
                db.session.commit()
                flash(f"Successfully removed {student.first_name} {student.last_name} from {scenario.name}.", "success")
            except Exception as e:
                db.session.rollback()
                flash("Error removing student from scenario.", "error")
        else:
            flash(f"{student.first_name} {student.last_name} is not assigned to this scenario.", "warning")
    
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
                flash(f"Successfully removed all {student_count} students from {scenario.name}.", "success")
            else:
                flash("No students were assigned to this scenario.", "info")
                
        except Exception as e:
            db.session.rollback()
            flash("Error removing students from scenario.", "error")
    
    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))

@views.route("/patients", methods=["GET"])
@login_required
def patient_dashboard():
    patients = Patient.query.all()
    delete_form = DeleteForm()  # one form instance reused
    return render_template("views/patient_dash.html", patients=patients, delete_form=delete_form)


@views.route("/patients/delete/<int:patient_id>", methods=["POST"])
@login_required
def delete_patient(patient_id):
    form = DeleteForm()
    if form.validate_on_submit():  # ✅ checks CSRF
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        flash("Patient deleted successfully!", "success")
    else:
        flash("CSRF check failed!", "danger")
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
        scenario_name = request.form.get('scenario_name', '').strip()
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
        question_text = request.form.get('question_text', '').strip()
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
        description = request.form.get('description', '').strip()
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
        patient_id = request.form.get('patient_id')
        if patient_id:
            patient = Patient.query.get_or_404(int(patient_id))
            scenario.active_patient_id = patient.id
            
            try:
                db.session.commit()
                flash(f"Successfully set {patient.first_name} {patient.last_name} as the active patient for this scenario.", "success")
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
                flash(f"Successfully removed {patient_name} as the active patient.", "success")
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
            name=f"Scenario {Scenario.query.count() + 1}",   # auto-number
            description="Basic ASL workflow practice",
            teacher_id=current_user.id,
            version=1
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
    scenario_ids = request.form.getlist('scenario_ids')
    
    if not scenario_ids:
        flash("No scenarios selected for deletion.", "error")
        return redirect(url_for("views.teacher_dashboard"))
    
    try:
        # Convert to integers and validate
        scenario_ids = [int(id) for id in scenario_ids]
        
        # Get scenarios and verify ownership
        scenarios = Scenario.query.filter(
            Scenario.id.in_(scenario_ids),
            Scenario.teacher_id == current_user.id
        ).all()
        
        if len(scenarios) != len(scenario_ids):
            flash("Some scenarios could not be found or you don't have permission to delete them.", "error")
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
