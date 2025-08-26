from flask import Blueprint, render_template, request, jsonify
from .models import db, Patient, Prescriber, Prescription, PrescriptionStatus, ConsentStatus, ASLStatus
from sqlalchemy import or_
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/asl/<int:pt>')
def asl(pt: int):
    """ASL page: show patient prescriptions"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        # Get available prescriptions
        asl_prescriptions = db.session.query(Prescription, Prescriber).join(
            Prescriber, Prescription.prescriber_id == Prescriber.id
        ).filter(
            Prescription.patient_id == pt,
            Prescription.status == PrescriptionStatus.AVAILABLE.value
        ).all()
        
        # Get dispensed ones for ALR section (show it)  
        alr_prescriptions = db.session.query(Prescription, Prescriber).join(
            Prescriber, Prescription.prescriber_id == Prescriber.id
        ).filter(
            Prescription.patient_id == pt,
            Prescription.status == PrescriptionStatus.DISPENSED.value
        ).all()
        
        
        # split medicare number (like the real system)
        medicare_full = patient.medicare or ""
        medicare_main = medicare_full[:9] if len(medicare_full) >= 9 else medicare_full 
        medicare_suffix = medicare_full[9:] if len(medicare_full) > 9 else ""
        
        pt_data = {
            # basic patient info
            "medicare": medicare_main,  
            "medicare-suffix": medicare_suffix,  # combination with the previous one
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
            
            # in order to make sure templates can still work, keep old filed names
            "name": patient.name,
            "dob": patient.dob,
            "address-1": patient.address_1,
            "address-2": patient.address_2,
            "asl_data": [],
            "alr_data": [],
            
            # UI status info
            "asl_status": patient.get_asl_status().name.replace('_', ' ').title(),
            "consent_status": patient.get_consent_status().name.title(),
            "consent_last_updated": patient.consent_last_updated.strftime('%d/%b/%Y %I:%M%p') if patient.consent_last_updated else "01/Jan/2000 02:59AM"
        }
        
        # create prescription data
        for prescription, prescriber in asl_prescriptions:
            #combine doctor name and title
            clinician_name_and_title = f"{prescriber.fname} {prescriber.lname}"
            if prescriber.title:
                clinician_name_and_title += f" {prescriber.title}"
            
            asl_item = {
                # to meet the front-end requirement
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
                
                # and new flat format for front-end use
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
        
        # Create ALR data 
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
                

                # Clinician info
                "clinician-name-and-title": clinician_name_and_title,
                "clinician-address-1": prescriber.address_1,
                "clinician-address-2": prescriber.address_2,
                "clinician-id": prescriber.prescriber_id,
                "hpii": prescriber.hpii,
                "hpio": prescriber.hpio,
                "clinician-phone": prescriber.phone,
                "clinician-fax": prescriber.fax,
                
                # to make sure the old template still works, keep the old format
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

# Interactive functions (refresh, request access, delete consent, search)
@views.route('/api/asl/<int:pt>/refresh', methods=['POST'])
def refresh_asl(pt: int):
    """Refresh Button"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        # update pending prescriptions
        updated_count = Prescription.query.filter_by(
            patient_id=pt,
            status=PrescriptionStatus.PENDING.value
        ).update({'status': PrescriptionStatus.AVAILABLE.value})
        

        db.session.commit()
        # to show that it works, need to modify it later
        return jsonify({
            'success': True,
            'message': f'ASL refreshed for patient {patient.name}. Updated {updated_count} prescriptions.',
            'updated_prescriptions': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/asl/<int:pt>/request-access', methods=['POST'])
def request_access(pt: int):
    """Request access Button"""
    try:
        patient = Patient.query.get_or_404(pt)
        
        if patient.asl_status == ASLStatus.REGISTERED.value:
            patient.asl_status = ASLStatus.ACCESS_REQUESTED.value
        elif patient.asl_status == ASLStatus.ACCESS_REQUESTED.value:
            patient.asl_status = ASLStatus.ACCESS_GRANTED.value
        else:
            patient.asl_status = ASLStatus.ACCESS_GRANTED.value
            
        db.session.commit()
        
        # need to modify the message later
        return jsonify({
            'success': True,
            'message': f'Access status updated for {patient.name}',
            'new_status': ASLStatus(patient.asl_status).name.replace('_', ' ').title()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/patient/<int:pt>/consent', methods=['DELETE'])
def delete_consent(pt: int):
    """Delete/revoke consent"""
    try:
        patient = Patient.query.get_or_404(pt)
        patient.consent_status = ConsentStatus.REVOKED.value
        patient.consent_last_updated = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Consent revoked for {patient.name}',
            'consent_status': ConsentStatus(patient.consent_status).name.title(),
            'last_updated': patient.consent_last_updated.strftime('%d/%b/%Y %I:%M%p')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@views.route('/api/asl/<int:pt>/search')
def search_asl(pt: int):
    """Search ASL prescriptions"""
    try:
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
def print_selected_prescriptions():
    """Print selected prescriptions from ASL"""
    try:
        prescription_ids = request.json.get('prescription_ids', [])
        
        if not prescription_ids:
            return jsonify({'success': False, 'error': 'No prescriptions selected'})
        
        prescriptions = Prescription.query.filter(
            Prescription.id.in_(prescription_ids)
        ).all()
        
        # format prescription data for printing 
        print_data = []
        for prescription in prescriptions:
            prescriber = prescription.prescriber
            patient = prescription.patient
            
            print_item = {
                # Patient info
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
                
                # Prescription info
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
                
                # Doctor info
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
        
        # modify it later
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