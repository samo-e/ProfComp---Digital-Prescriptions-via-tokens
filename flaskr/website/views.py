from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "index"

@views.route('/dashboard')
def dashboard():
    user_type = "Teacher" # "Student"/"Teacher"
    scenarios = [
        {
            "id" : 286401,
            "name" : "Scenario Imaginative Name 1",
            "user-attempts-count" : 3,
            "num-students" : 250,
            "num-students-completed" : 100,
            "creation-date" : "11/10/2020",
            "due-date" : "18/10/2020",
        },
        {
            "id" : 495050,
            "name" : "Scenario Great Name",
            "user-attempts-count" : 7,
            "num-students" : 345,
            "num-students-completed" : 143,
            "creation-date" : "11/10/2020",
            "due-date" : "18/10/2020",
        },
        {
            "id" : 495051,
            "name" : "Scenario Hello World",
            "user-attempts-count" : 1,
            "num-students" : 600,
            "num-students-completed" : 600,
            "creation-date" : "11/10/2020",
            "due-date" : "18/10/2020",
        },
        {
            "id" : 634524,
            "name" : "Finale",
            "user-attempts-count" : 0,
            "num-students" : 78,
            "num-students-completed" : 9,
            "creation-date" : "11/10/2020",
            "due-date" : "18/10/2020",
        },
    ]
    return render_template("views/dashboard.html", user_type=user_type, scenarios=scenarios)

@views.route('/asl/<pt>') # I imagine each ASL would be accessed by the patient's IHI
def asl(pt: int):
    pt_data = { 
        "medicare" : 49502864011,
        "pharmaceut-ben-entitlement-no" : "NA318402K(W)",
        "sfty-net-entitlement-cardholder" : True,
        "rpbs-ben-entitlement-cardholder" : False,
        "name" : "Draga Diaz",
        "dob" : "26/01/1998",
        "preferred-contact" : "0401 234 567",
        "address-1" : "33 JIT DR",
        "address-2" : "CHARAM VIC 3318",
        "script-date" : "30/11/2020",
        "pbs" : None,
        "rpbs" : None,
        "asl_data" : [
            {
                "prescriber" : {
                    "fname" : "Phillip",
                    "lname" : "Davis",
                    "title" : "( MBBS; FRACGP )",
                    "address-1" : "Level 3  60 Albert Rd",
                    "address-2" : "SOUTH MELBOURNE VIC 3205", 
                    "id" : 987774,
                    "hpii" : 8003619900026805,
                    "hpio" : 8003626566692846,
                    "phone" : "03 9284 3300",
                    "fax" : None,
                },
                "DSPID" : "MPK00009002011563",
                "status" : "Available",
                "brand-sub-not-prmt" : False,
                "drug-name"  : "Coversyl 5mg tablet, 30 5 mg 30 Tablets",
                "drug-code"  : "9007C",
                "dose-instr" : "ONCE A DAY",
                "dose-qty"   : 30,
                "dose-rpt"   : 6,
                "prescribed-date" : "10/06/2021",
                "paperless" : True,
            },
            {
                "prescriber" : {
                    "fname" : "Phillip",
                    "lname" : "Davis",
                    "title" : "( MBBS; FRACGP )",
                    "address-1" : "Level 3  60 Albert Rd",
                    "address-2" : "SOUTH MELBOURNE VIC 3205", 
                    "id" : 987774,
                    "hpii" : 8003619900026805,
                    "hpio" : 8003626566692846,
                    "phone" : "03 9284 3300",
                    "fax" : None,
                },
                "DSPID" : "MPK00009002020646",
                "status" : "Available",
                "brand-sub-not-prmt" : False,
                "drug-name"  : "Diabex 1 g tablet, 90 1000 mg 90 Tablets",
                "drug-code"  : "8607B",
                "dose-instr" : "ONCE A DAY",
                "dose-qty"   : 90,
                "dose-rpt"   : 6,
                "prescribed-date" : "10/06/2021",
                "paperless" : True,
            },
            {
                "prescriber" : {
                    "fname" : "Phillip",
                    "lname" : "Davis",
                    "title" : "( MBBS; FRACGP )",
                    "address-1" : "Level 3  60 Albert Rd",
                    "address-2" : "SOUTH MELBOURNE VIC 3205", 
                    "id" : 987774,
                    "hpii" : 8003619900026805,
                    "hpio" : 8003626566692846,
                    "phone" : "03 9284 3300",
                    "fax" : None,
                },
                "DSPID" : None,
                "status" : "Available",
                "brand-sub-not-prmt" : False,
                "drug-name"  : "Lipitor 10mg tablet, 30 10 mg 30 Tablets",
                "drug-code"  : "8213G",
                "dose-instr" : "ONCE A DAY",
                "dose-qty"   : 30,
                "dose-rpt"   : 5,
                "prescribed-date" : "10/06/2021",
                "paperless" : False,
            },
        ],
        "alr_data" : [
            {
                "prescriber" : {
                    "fname" : "Phillip",
                    "lname" : "Davis",
                    "title" : "( MBBS; FRACGP )",
                    "address-1" : "Level 3  60 Albert Rd",
                    "address-2" : "SOUTH MELBOURNE VIC 3205", 
                    "id" : 987774,
                    "hpii" : 8003619900026805,
                    "hpio" : 8003626566692846,
                    "phone" : "03 9284 3300",
                    "fax" : None,
                },
                "DSPID" : None,
                "drug-name"  : "Levlen ED Tablets, 150mcg-30mcg(28)",
                "drug-code"  : "1394J",
                "dose-instr" : "",
                "dose-qty"   : 4,
                "dose-rpt"   : 2,
                "prescribed-date" : "05/07/2021",
                "dispensed-date" : "05/07/2021",
                "paperless" : False,
            },
            {
                "prescriber" : {
                    "fname" : "Phillip",
                    "lname" : "Davis",
                    "title" : "( MBBS; FRACGP )",
                    "address-1" : "Level 3  60 Albert Rd",
                    "address-2" : "SOUTH MELBOURNE VIC 3205", 
                    "id" : 987774,
                    "hpii" : 8003619900026805,
                    "hpio" : 8003626566692846,
                    "phone" : "03 9284 3300",
                    "fax" : None,
                },
                "DSPID" : None,
                "drug-name"  : "Diabex 1 g tablet, 90 1000 mg 90 Tablets",
                "drug-code"  : "8607B",
                "dose-instr" : "Shake well and inhale TWO puffs by mouth TWICE a day as directed by your physician",
                "dose-qty"   : 1,
                "dose-rpt"   : 3,
                "prescribed-date" : "10/06/2021",
                "dispensed-date" : "23/06/2021",
                "paperless" : True,
            },
        ],
    }
    return render_template("views/asl.html", pt=pt, pt_data=pt_data)

@views.route('/prescription') # I imagine each ASL would be accessed by the patient's IHI
def prescription():
    return render_template("views/prescription/prescription.html")

@views.route('/edit-pt/<pt>') # I imagine each ASL would be accessed by the patient's IHI
def edit_pt(pt: int):
    return render_template("views/edit_pt.html", pt=pt)

@views.route('/edit-scenario/<int:scenario>')
def edit_scenario(scenario: int): # POST and GET
    # Check person has access to scenario
    scenario_data = {}
    #if not scenario.exists(): # New scenario
    #    scenario_data = None
    return render_template("views/edit_scenario.html", scenario_data=scenario_data)

@views.route('/attempt-scenario/<int:scenario>')
def attempt_scenario(scenario: int): # POST and GET
    # Check person has access to scenario
    scenario_data = {}
    return render_template("views/attempt_scenario.html", scenario_data=scenario_data)

@views.route('/export-scenario/<int:scenario>')
def export_scenario(scenario: int): # GET
    # Check person has access to scenario
    scenario_data = f"scenario-{scenario}.csv"
    return scenario_data

@views.route('/delete-scenario/<int:scenario>')
def delete_scenario(scenario: int): # POST
    # Check person has access to scenario
    return 204
