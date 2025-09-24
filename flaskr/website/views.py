
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify,request
from .forms import PatientForm,ASLForm
from flask_login import login_required, current_user
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ASLStatus, ASL
from sqlalchemy import or_
from datetime import datetime
import requests

views = Blueprint('views', __name__)

@views.route('/student_dashboard')
@login_required 
def student_dashboard():
    if not current_user.role.value == "student":
        flash("Access denied: Students only.", "error")
        return redirect(url_for('views.teacher_dashboard'))
    return render_template("views/student_dashboard.html")

@views.route('/teacher_dashboard')
@login_required 
def teacher_dashboard():
    if not current_user.role.value == "teacher":
        flash("Access denied: Teachers only.", "error")
        return redirect(url_for('views.student_dashboard'))
    return render_template("views/teacher_dash.html")

@views.route('/scenario/<int:scenario_id>/set_current/<int:patient_id>', methods=["POST"])
def set_current_patient(scenario_id, patient_id):
    # clear existing current patient (if you only allow one)
    Patient.query.update({Patient.asl_status: None})  # or use a separate column like is_current

    # mark this patient as current
    patient = Patient.query.get(patient_id)
    patient.asl_status = "current"   # or patient.is_current = True if you added that column
    db.session.commit()

    flash(f"Patient {patient.name} set as current!", "success")
    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))

@views.route('/scenario/<int:scenario_id>/dashboard')
def scenario_dashboard(scenario_id):
    patients = Patient.query.all()

    # pick the first patient with status=current (or use is_current flag)
    current_patient = Patient.query.filter_by(asl_status="current").first()

    return render_template(
        "views/scenario_dashboard.html",
        scenario_id=scenario_id,
        patients=patients,
        current_patient=current_patient
    )

@views.route('/scenario/<int:scenario_id>/create_patient')
def create_patient(scenario_id):
    return f"<h1>Create Patient Page for Scenario {scenario_id}</h1>"

  
@views.route('/edit-pt/<int:scenario_id>', methods=["GET", "POST"])
def edit_pt(scenario_id):
    patient = Patient.query.first()  # later filter by scenario_id
    form = PatientForm(obj=patient)

    if form.validate_on_submit():
        # if patient exists, update it; else, create new
        if not patient:
            patient = Patient()

        # Basic details
        patient.last_name   = form.basic.lastName.data
        patient.given_name  = form.basic.givenName.data
        patient.title       = form.basic.title.data
        patient.sex         = form.basic.sex.data
        patient.dob         = form.basic.dob.data.strftime("%d/%m/%Y") if form.basic.dob.data else None
        patient.pt_number   = form.basic.ptNumber.data

        # Contact
        patient.address     = request.form.get("basic-address")  # since address is raw input in HTML
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

        flash("Patient saved successfully!", "success")
        return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))
    else:
        print(form.errors)

    return render_template("views/edit_pt.html", form=form, scenario_id=scenario_id)

@views.route("/patients")
def list_patients():
    patients = Patient.query.all()
    rows = []
    for p in patients:
        rows.append(
            f"id={p.id}, last_name={p.last_name}, given_name={p.given_name}, "
            f"DOB={p.dob}, Medicare={p.medicare}, Suburb={p.suburb}, State={p.state}"
        )
    return "<br>".join(rows)




@views.route('/scenario/<int:scenario_id>/delete-pt/<int:patient_id>', methods=["POST", "GET"])
def delete_pt(scenario_id, patient_id):
    patient = Patient.query.get_or_404(patient_id)
    
    db.session.delete(patient)
    db.session.commit()

    flash("Patient deleted successfully!", "success")
    return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))




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
    """ASL page: show patient prescriptions"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        # Check if we can view this patient's ASL based on asl_status
        can_view_asl = patient.can_view_asl()
        
        # users can get prescriptions if they have access
        asl_prescriptions = []
        alr_prescriptions = []
        
        if can_view_asl:
            # AVAILABLE prescriptions only for ASL table
            asl_prescriptions = db.session.query(Prescription, Prescriber).join(
                Prescriber, Prescription.prescriber_id == Prescriber.id
            ).filter(
                Prescription.patient_id == pt,
                Prescription.status == PrescriptionStatus.AVAILABLE.value  # Only AVAILABLE show in ASL
            ).all()
            
            # ALR prescriptions
            alr_prescriptions = db.session.query(Prescription, Prescriber).join(
                Prescriber, Prescription.prescriber_id == Prescriber.id
            ).filter(
                Prescription.patient_id == pt,
                Prescription.status == PrescriptionStatus.DISPENSED.value,
                Prescription.dispensed_at_this_pharmacy == True,  # Only from this pharmacy
                Prescription.remaining_repeats > 0  # only show remaining repeats
            ).all()
        
        medicare_full = patient.medicare or ""
        medicare_main = medicare_full[:9] if len(medicare_full) >= 9 else medicare_full 
        medicare_suffix = medicare_full[9:] if len(medicare_full) > 9 else ""
        
        pt_data = {
            "medicare": medicare_main,  
            "medicare-suffix": medicare_suffix,
            "pharmaceut-ben-entitlement-no": patient.pharmaceut_ben_entitlement_no,
            "sfty-net-entitlement-cardholder": patient.sfty_net_entitlement_cardholder,
            "rpbs-ben-entitlement-cardholder": patient.rpbs_ben_entitlement_cardholder,
            "pt-name": patient.name,  
            "pt-dob": patient.dob,   
            "preferred-contact": patient.preferred_contact,
            "pt-address-1": patient.address_1,  
            "pt-address-2": patient.address_2,
            "script-date": patient.script_date,
            "pbs": patient.pbs,
            "rpbs": patient.rpbs,
            "brand-sub-not-prmt": None, 
            
            "name": patient.name,
            "dob": patient.dob,
            "address-1": patient.address_1,
            "address-2": patient.address_2,
            "asl_data": [],
            "alr_data": [],
            
            # UI status info
            "asl_status": patient.get_asl_status().name.replace('_', ' ').title(),
            "consent_last_updated": patient.consent_last_updated if patient.consent_last_updated else "01/Jan/2000 02:59AM",
            # Add access control flag 
            "can_view_asl": can_view_asl
        }
        
        for prescription, prescriber in asl_prescriptions:
            #combine doctor name and title
            clinician_name_and_title = f"{prescriber.fname} {prescriber.lname}"
            if prescriber.title:
                clinician_name_and_title += f" {prescriber.title}"
            
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
                
                "clinician-name-and-title": clinician_name_and_title,
                "clinician-address-1": prescriber.address_1,
                "clinician-address-2": prescriber.address_2,
                "clinician-id": prescriber.prescriber_id,
                "hpii": prescriber.hpii,
                "hpio": prescriber.hpio,
                "clinician-phone": prescriber.phone,
                "clinician-fax": prescriber.fax,
                "dose-freq": prescription.dose_instr, 
            }
            pt_data["asl_data"].append(asl_item)
        
        for prescription, prescriber in alr_prescriptions:
            clinician_name_and_title = f"{prescriber.fname} {prescriber.lname}"
            if prescriber.title:
                clinician_name_and_title += f" {prescriber.title}"
                
            alr_item = {
                "prescription_id": prescription.id,
                "DSPID": prescription.DSPID,
                "drug-name": prescription.drug_name,
                "drug-code": prescription.drug_code,
                "dose-instr": prescription.dose_instr,
                "dose-freq": prescription.dose_instr,
                "dose-qty": prescription.dose_qty,
                "dose-rpt": prescription.dose_rpt,
                "prescribed-date": prescription.prescribed_date,
                "dispensed-date": prescription.dispensed_date,
                "paperless": prescription.paperless,
                "brand-sub-not-prmt": prescription.brand_sub_not_prmt,
                # Show remaining repeats for ALR 
                "remaining-repeats": prescription.remaining_repeats,
                
                "clinician-name-and-title": clinician_name_and_title,
                "clinician-address-1": prescriber.address_1,
                "clinician-address-2": prescriber.address_2,
                "clinician-id": prescriber.prescriber_id,
                "hpii": prescriber.hpii,
                "hpio": prescriber.hpio,
                "clinician-phone": prescriber.phone,
                "clinician-fax": prescriber.fax,
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
            pt_data["alr_data"].append(alr_item)
        
        return render_template("views/asl.html", pt=pt, pt_data=pt_data)
        
    except Exception as e:
        return f"Error loading ASL data: {str(e)}", 500

# Enhanced refresh function
@views.route('/api/asl/<int:pt>/refresh', methods=['POST'])
def refresh_asl(pt: int):
    try:
        patient = Patient.query.get_or_404(pt)
        
        # Handle different ASL statuses
        if patient.asl_status == ASLStatus.PENDING.value:
            # Simulate patient replying to SMS/email (for this demo, it will auto-approve)
            patient.asl_status = ASLStatus.GRANTED.value
            patient.consent_last_updated = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
            
            # update any PENDING prescriptions to AVAILABLE
            updated_count = Prescription.query.filter_by(
                patient_id=pt,
                status=PrescriptionStatus.PENDING.value
            ).update({'status': PrescriptionStatus.AVAILABLE.value})
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Patient {patient.name} replied and granted access! {updated_count} prescriptions now available.',
                'updated_prescriptions': updated_count,
                'should_reload': True
            })
            
        elif patient.asl_status == ASLStatus.GRANTED.value:
            # For GRANTED status, just check for new PENDING prescriptions
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
            # Handle NO_CONSENT and REJECTED statuses
            return jsonify({
                'success': False,
                'error': f'Cannot refresh ASL - status is {patient.get_asl_status().name.replace("_", " ").title()}'
            }), 403
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Update request access function
@views.route('/api/asl/<int:pt>/request-access', methods=['POST'])
def request_access(pt: int):
    try:
        patient = Patient.query.get_or_404(pt)
        current_status = patient.get_asl_status()
        
        # Only allow request from NO_CONSENT status (others' buttons would be grey)
        if current_status != ASLStatus.NO_CONSENT:
            return jsonify({
                'success': False,
                'error': f'Cannot request access - current status is {current_status.name.replace("_", " ").title()}'
            }), 400
        
        # Change NO_CONSENT to PENDING (simulate sending SMS/email)
        patient.asl_status = ASLStatus.PENDING.value
        patient.consent_last_updated = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Access request sent to {patient.name}. Patient will receive SMS/email to approve.',
            'new_status': 'Pending',
            'should_disable_button': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Update delete consent function (reset to no consent)
@views.route('/api/patient/<int:pt>/consent', methods=['DELETE'])
def delete_consent(pt: int):
    try:
        patient = Patient.query.get_or_404(pt)
        
        # Reset to NO_CONSENT
        patient.asl_status = ASLStatus.NO_CONSENT.value
        patient.consent_last_updated = datetime.utcnow().strftime('%d/%m/%Y %H:%M')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Consent record deleted for {patient.name}. Can now request access again.',
            'new_status': 'No Consent',
            'should_reload': True
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Access control to search function
@views.route('/api/asl/<int:pt>/search')
def search_asl(pt: int):
    try:
        patient = Patient.query.get_or_404(pt)
        
        # Check access before allowing search
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

# Access control to print function
@views.route('/api/prescriptions/print-selected', methods=['POST'])
def print_selected_prescriptions():
    try:
        prescription_ids = request.json.get('prescription_ids', [])
        
        if not prescription_ids:
            return jsonify({'success': False, 'error': 'No prescriptions selected'})
        
        prescriptions = Prescription.query.filter(
            Prescription.id.in_(prescription_ids)
        ).all()
        
        # Check access for each patient
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
                "pt-name": patient.name,
                "pt-dob": patient.dob,
                "preferred-contact": patient.preferred_contact,
                "pt-address-1": patient.address_1,
                "pt-address-2": patient.address_2,
                "script-date": patient.script_date,
                "pbs": patient.pbs,
                "rpbs": patient.rpbs,
                
                "prescription_id": prescription.id,
                "DSPID": prescription.DSPID,
                "status": prescription.get_status().name.title(),
                "drug-name": prescription.drug_name,
                "drug-code": prescription.drug_code,
                "dose-instr": prescription.dose_instr,
                "dose-freq": prescription.dose_instr,
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
def prescription():
    """Printing pdf"""
    return render_template("views/prescription/prescription.html")

@views.route('/scenario/<int:scenario_id>/patient/<int:patient_id>/asl', methods=["GET", "POST"])
def patient_asl_form(scenario_id, patient_id):
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
        return redirect(url_for("views.scenario_dashboard", scenario_id=scenario_id))

    return render_template(
        "views/patientasl.html",
        form=form,
        patient=patient,
        scenario_id=scenario_id
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

