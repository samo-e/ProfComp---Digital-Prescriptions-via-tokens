from flask import Blueprint, render_template, request, jsonify
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ASLStatus
from sqlalchemy import or_
from datetime import datetime

views = Blueprint('views', __name__)

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