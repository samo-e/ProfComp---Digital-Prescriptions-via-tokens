from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return "index"

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