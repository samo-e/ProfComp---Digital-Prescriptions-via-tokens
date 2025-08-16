from flask import Flask, render_template

app = Flask(__name__, template_folder=".")

@app.route("/")
def index():
    return render_template("edit_pts/edit_pt.html")

if __name__ == "__main__":
    app.run(debug=True)