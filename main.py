from flask import Flask, render_template, request, url_for, flash
import sqlite3
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__, template_folder="template")
app.secret_key = "supersecretkey"


# Database setup
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM news ORDER BY news_id Asc")
    newss = cur.fetchall()
    con.close()
    print(f"DEBUG: Retrieved rows:{newss}")
    return render_template("index.html", newss=newss)


@app.route("/login.html")
def login():
    return render_template("login.html")


@app.route("/map.html")
def map():
    return render_template("map.html")


@app.route("/online__tickets.html")
def online__tickets():
    return render_template("online__tickets.html")


@app.route("/blocked__cars.html")
def blocked__cars():
    return render_template("blocked__cars.html")


@app.route("/mayor.html")
def mayor():
    return render_template("mayor.html")


@app.route("/complaints.html")
def complaints():
    return render_template("complaints.html")


@app.route("/emergency.html")
def emergency():
    return render_template("emergency.html")


@app.route("/blog.html", methods=["POST", "GET"])
def blog():
    msg = ""
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM blog ORDER BY blog_id DESC")
    posts = cur.fetchall()
    con.close()

    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM reply_blog")
    replyposts = cur.fetchall()
    con.close()

    if request.method == "POST":
        try:
            citizen_id = request.form["citizen_id"]
            description = request.form["reply"]
            blog_id = request.form["id"]
            with get_db_connection() as con:
                cur = con.cursor()

                cur.execute(
                    "SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,)
                )
                citizen = cur.fetchone()

                if citizen:
                    cur.execute(
                        "SELECT name FROM citizens WHERE citizen_id = ?", (citizen_id,)
                    )
                    name = cur.fetchone()
                    name_reply = dict(name)
                    name_reply = name_reply["name"]

                    cur.execute(
                        "INSERT INTO reply_blog (blog_id, name_reply, description) VALUES ( ?, ?, ?)",
                        (blog_id, name_reply, description),
                    )
                    con.commit()
                    msg = "Record successfully added"
                    print(
                        f"DEBUG: Inserted {blog_id}, {name_reply}, {description} into reply_blog table"
                    )
                    return render_template(url_for("blog"))
                else:
                    msg = "Citizen ID not found, please try again."
                    flash("Citizen ID not found, please try again.", "error")
        except Exception as e:
            con.rollback()
            print(f"DEBUG: Error in insert operation: {e}")

    print(f"DEBUG: Retrieved rows:{posts}")
    return render_template("blog.html", posts=posts, replyposts=replyposts, msg=msg)


@app.route("/add_blog.html", methods=["POST", "GET"])
def add_blog():
    msg = ""
    if request.method == "POST":
        try:
            citizen_id = request.form["citizen_id"]
            description = request.form["description"]
            current_time = datetime.now().strftime("%Y-%m-%d")

            with get_db_connection() as con:
                cur = con.cursor()

                cur.execute(
                    "SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,)
                )
                citizen = cur.fetchone()

                cur.execute(
                    "SELECT name FROM citizens WHERE citizen_id = ?", (citizen_id,)
                )
                name = cur.fetchone()
                name_blog = dict(name)
                name_blog = name_blog["name"]

                if citizen:
                    cur.execute(
                        "INSERT INTO blog (name_blog, description, date_added) VALUES ( ?, ?, ?)",
                        (name_blog, description, current_time),
                    )
                    con.commit()
                    msg = "Record successfully added"
                    print(
                        f"DEBUG: Inserted {citizen_id}, {description}, {current_time} into blog table"
                    )
                else:
                    msg = "Citizen ID not found, please try again."
                    flash("Citizen ID not found, please try again.", "error")
        except Exception as e:
            con.rollback()
            print(f"DEBUG: Error in insert operation: {e}")
    return render_template("add_blog.html", msg=msg)


@app.route("/transportation.html")
def transportation():
    return render_template("transportation.html")


@app.route("/skill__sharing.html")
def skill__sharing():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM skill_sharing ORDER BY ss_id DESC")
    rows = cur.fetchall()
    con.close()

    posts = []
    for row in rows:
        post = dict(row)
        if post["type"] == "plumbing":
            post["type_image"] = "plumbing.png"
        elif post["type"] == "electrical":
            post["type_image"] = "electrical.png"
        elif post["type"] == "furniture":
            post["type_image"] = "furniture.png"
        else:
            post["type_image"] = "other.png"
        posts.append(post)

    print(f"DEBUG: Retrieved rows:{posts}")
    return render_template("skill__sharing.html", posts=posts, type_image=posts)


@app.route("/add_skill_sharing.html", methods=["POST", "GET"])
def add_skill_sharing():
    return render_template("add_skill_sharing.html")


app.config["UPLOAD_FOLDER"] = "static/ss_images"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # Adjust this as necessary


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/add_skill_sharing_post", methods=["POST", "GET"])
def add_skill_sharing_post():
    msg = ""
    if request.method == "POST":
        try:
            citizen_id = request.form["citizen_id"]
            type = request.form["type"]
            description = request.form["description"]
            phone = request.form["phone"]
            email = request.form["email"]
            pic = request.files["pic"]
            current_time = datetime.now().strftime("%Y-%m-%d")

            with get_db_connection() as con:
                cur = con.cursor()

                cur.execute(
                    "SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,)
                )
                citizen = cur.fetchone()

                if citizen:
                    if pic and allowed_file(pic.filename):
                        filename = secure_filename(pic.filename)
                        pic.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    else:
                        filename = "defult_ss.png"

                    cur.execute(
                        "INSERT INTO skill_sharing (citizen_id, description, phone, email, type, img_name, date_added) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (
                            citizen_id,
                            description,
                            phone,
                            email,
                            type,
                            filename,
                            current_time,
                        ),
                    )
                    con.commit()
                    msg = "Record successfully added"
                    print(
                        f"DEBUG: Inserted {citizen_id}, {type}, {email}, {description}, {phone}, {filename}, {current_time} into skill_sharing table"
                    )
                else:
                    msg = "Citizen ID not found, please try again."
                    flash("Citizen ID not found, please try again.", "error")

        except Exception as e:
            con.rollback()
            print(f"DEBUG: Error in insert operation: {e}")
    return render_template("add_skill_sharing.html", msg=msg)


@app.route("/digital__voting.html")
def digital__voting():
    return render_template("digital__voting.html")


@app.route("/online-tickets/bills.html")
def bills():
    return render_template("/online-tickets/bills.html")


@app.route("/online-tickets/can_request.html")
def can_request():
    return render_template("/online-tickets/can_request.html")


@app.route("/online-tickets/earthquake.html")
def earthquake():
    return render_template("/online-tickets/earthquake.html")


@app.route("/online-tickets/garbage.html")
def garbage():
    return render_template("/online-tickets/garbage.html")


@app.route("/online-tickets/reward_points.html")
def reward_points():
    return render_template("/online-tickets/reward_points.html")


@app.route("/online-tickets/sewege.html")
def sewege():
    return render_template("/online-tickets/sewege.html")


@app.route("/online-tickets/Spraying.html")
def Spraying():
    return render_template("/online-tickets/Spraying.html")


@app.route("/online-tickets/tree_pruning.html")
def tree_pruning():
    return render_template("/online-tickets/tree_pruning.html")


# Route to handle the voting process
@app.route("/vote/<vote_id>.html", methods=["GET", "POST"])
def vote(vote_id):
    if request.method == "POST":
        try:
            citizen_id = request.form["citizen_id"]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with get_db_connection() as conn:
                cur = conn.cursor()
                # Check if the vote already exists
                cur.execute(
                    "SELECT * FROM votes WHERE vote_id = ? AND citizen_id = ?",
                    (vote_id, citizen_id),
                )
                existing_vote = cur.fetchone()
                if existing_vote:
                    flash("You have already voted for this option.", "error")
                else:
                    # Check if the citizen exists
                    # cur.execute("SELE* FROM citizens WHERE citizen_id = ?", (citizen_id,))
                    cur.execute(
                        "SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,)
                    )
                    citizen = cur.fetchone()

                    if citizen:
                        cur.execute(
                            "INSERT INTO votes (vote_id, citizen_id, date) VALUES (?, ?, ?)",
                            (vote_id, citizen_id, current_time),
                        )
                        conn.commit()
                        flash("Vote submitted successfully!", "success")
                    else:
                        flash("Citizen ID not found, please try again.", "error")
        except Exception as e:
            flash(f"Error submitting vote: {e}", "error")

    # Pass the vote_id to the vote.html template
    return render_template("vote.html", vote_id=vote_id)


if __name__ == "__main__":
    app.run(debug=True, port=4500)
