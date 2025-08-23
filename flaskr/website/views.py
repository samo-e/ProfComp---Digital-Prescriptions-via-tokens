from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "index"

@views.route('/dashboard')
def teacher_dashboard():
    return render_template("views/teacher_dash.html")

@views.route('/scenario/<id>')
def scenario_edit(id: int):
    print("not implemented")

@views.route('/asl/<pt>') # I imagine each ASL would be accessed by the patient's IHI
def asl(pt: int):
    pt_data = {
        "clinician-name-and-title" : "Phillip Davis ( MBBS; FRACGP )",
        "clinician-address-1" : "Level 3  60 Albert Rd",
        "clinician-address-2" : "SOUTH MELBOURNE VIC 3205",  
        "DSPID" : "MPK00009002011563",
        "status" : "Available",
        "clinician-id" : 987774,
        "hpii" : 8003619900026805,
        "hpio" : 8003626566692846,
        "clinician-phone" : "03 9284 3300",
        "clinician-fax" : None,
        "medicare" : 49502864011,
        "pharmaceut-ben-entitlement-no" : "NA318402K(W)",
        "sfty-net-entitlement-cardholder" : True,
        "rpbs-ben-entitlement-cardholder" : False,
        "pt-name" : "Draga Diaz (26/01/1998 - 23yrs)",
        "pt-address-1" : "33 JIT DR",
        "pt-address-2" : "CHARAM VIC 3318",
        "script-date" : "30/11/2020",
        "pbs" : None,
        "rpbs" : None,
        "brand-sub-not-prmt" : False,
        "asl_data" : [{}],
        "alr_data" : [{}],
    }
    return render_template("views/asl.html", pt=pt, pt_data=pt_data)

@views.route('/prescription') # I imagine each ASL would be accessed by the patient's IHI
def prescription():
    return render_template("views/prescription/prescription.html")

@views.route('/edit-pt/<pt>') # I imagine each ASL would be accessed by the patient's IHI
def edit_pt(pt: int):
    return render_template("views/edit_pt.html")
