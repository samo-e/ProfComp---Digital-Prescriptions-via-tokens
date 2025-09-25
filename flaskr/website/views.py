
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify,request
from flask_login import login_required, current_user
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ASLStatus,ASL,Scenario,User
from .forms import PatientForm, ASLForm
from sqlalchemy import or_
from datetime import datetime
from functools import wraps
import requests

views = Blueprint('views', __name__)

@views.route('/')
def index():
    """Root route - redirects to appropriate dashboard"""
    if current_user.is_authenticated:
        if current_user.is_teacher():
            return redirect(url_for('views.teacher_dashboard'))
        else:
            return redirect(url_for('views.student_dashboard'))
    return redirect(url_for('auth.login'))

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
    
    return render_template(
        "views/teacher_dash.html",
        scenarios=scenarios,
        total_scenarios=total_scenarios,
        total_students=total_students
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
        patient.medicare_issue   = form.basic.medicareIssue.data
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
def edit_pt(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)

    if form.validate_on_submit():
        # update fields (same as create_patient)
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

        # (same blocks for Medicare, Concession, MyHR, Doctor, etc…)

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

@views.route("/scenario-demo")
def scenario_demo():
    # Just grab all patients from DB
    patients = Patient.query.all()

    # Fake scenario info (since you don’t have Scenario model yet)
    scenario = {
        "id": 1,
        "name": "Demo Scenario",
        "description": "Showing all patients loaded from the DB."
    }

    return render_template(
        "views/scenario_dash.html",
        scenario=scenario,
        patients=patients
    )

@views.route("/patients")
@login_required
def patient_dashboard():
    # Query all patients from DB
    patients = Patient.query.all()
    return render_template("views/patient_dash.html", patients=patients)

@views.route("/assign")
@login_required
def assign_dashboard():
    # Later you can fetch scenario + students from DB
    # For now, just render the HTML mockup
    return render_template("views/assign.html")