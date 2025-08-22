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
    return render_template("views/asl.html")

@views.route('/edit-pt/<pt>') # I imagine each ASL would be accessed by the patient's IHI
def edit_pt(pt: int):
    return render_template("views/edit_pt.html")

@views.route('/show-users')
def show_users():
    from .models import User
    users = User.query.all()
    return '<br>'.join([
        f'ID: {u.id} | Username: {u.username} | Email: {u.email} | Password: {u.password} | Role: {u.role}'
        for u in users
    ])