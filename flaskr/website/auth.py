from flask import request, Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route('/home')
def home():
    return "home"

@auth.route('/login', methods=["GET", "POST"])
def login():
    valid_password = True
    submitted_data = None

    if request.method == "POST":
        submitted_data = request.form.to_dict()
        print(submitted_data)
        password = request.form.get("password")
        if password != "secret123":
            valid_password = False

    return render_template(
        "auth/login.html",
        valid_password=valid_password,
        submitted_data=submitted_data
    )

@auth.route('/signup', methods=["GET", "POST"])
def signup():
    valid_password = True
    submitted_data = None
    
    # Need to do something similar to above

    return render_template(
        "auth/signup.html",
        valid_password=valid_password,
        submitted_data=submitted_data
    )

@auth.route('/logout')
def logout():
    return "logout"

