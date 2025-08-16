from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("edit_pts/edit_pt.html")

@app.route("/edit_pts/edit_pt.css")
def edit_pt_css():
    return send_from_directory(os.path.join(app.root_path, "edit_pts"), "edit_pt.css")

if __name__ == "__main__":
    app.run(debug=True)