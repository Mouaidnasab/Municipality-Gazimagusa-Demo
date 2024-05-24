from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder='templates_admin')
app.secret_key = 'supersecretkey'


# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/voting")
def voting():
    return render_template("voting.html")

# Route to form used to add a new citizen to the database
@app.route("/enternew")
def enternew():
    return render_template("citizen.html")

# Route to add a new record (INSERT) citizen data to the database
@app.route("/addrec", methods=['POST'])
def addrec():
    if request.method == 'POST':
        try:
            citizen_id = request.form['citizen_id']
            name = request.form['name']
            email = request.form['email']
            address = request.form['address']

            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("INSERT INTO citizens (citizen_id, name, email, address) VALUES (?, ?, ?, ?)",
                            (citizen_id, name, email, address))
                con.commit()
                msg = "Record successfully added"
                print(f"DEBUG: Inserted {citizen_id}, {name}, {email}, {address} into citizens table")
        except Exception as e:
            con.rollback()
            msg = f"Error in insert operation: {e}"
            print(f"DEBUG: Error in insert operation: {e}")

        finally:
            con.close()
            flash(msg)
            return redirect(url_for('list'))

# Route to list all citizens
@app.route("/list")
def list():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM citizens")
    rows = cur.fetchall()
    con.close()
    print(f"DEBUG: Retrieved rows: {rows}")
    return render_template("list.html", rows=rows)

# Route to edit a citizen
@app.route("/edit", methods=['POST', 'GET'])
def edit():
    if request.method == 'POST':
        citizen_id = request.form['id']
        con = get_db_connection()
        cur = con.cursor()
        cur.execute("SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,))
        rows = cur.fetchall()
        con.close()
        return render_template("edit.html", rows=rows)

# Route to update a citizen record
@app.route("/editrec", methods=['POST'])
def editrec():
    if request.method == 'POST':
        try:
            citizen_id = request.form['citizen_id']
            name = request.form['name']
            email = request.form['email']
            address = request.form['address']

            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("UPDATE citizens SET name = ?, email = ?, address = ? WHERE citizen_id = ?",
                            (name, email, address, citizen_id))
                con.commit()
                msg = "Record successfully updated"
        except Exception as e:
            con.rollback()
            msg = f"Error in update operation: {e}"

        finally:
            con.close()
            flash(msg)
            return redirect(url_for('list'))

# Route to delete a citizen
@app.route("/delete", methods=['POST'])
def delete():
    if request.method == 'POST':
        try:
            citizen_id = request.form['id']
            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM citizens WHERE citizen_id = ?", (citizen_id,))
                con.commit()
                msg = "Record successfully deleted"
        except Exception as e:
            con.rollback()
            msg = f"Error in delete operation: {e}"

        finally:
            con.close()
            flash(msg)
            return redirect(url_for('list'))

# Route to handle the voting process
@app.route("/vote", methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        try:
            vote_id = request.form['vote_id']
            citizen_id = request.form['citizen_id']
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with get_db_connection() as conn:
                cur = conn.cursor()
                
                # Check if the vote already exists
                cur.execute("SELECT * FROM votes WHERE vote_id = ? AND citizen_id = ?", (vote_id, citizen_id))
                existing_vote = cur.fetchone()
                
                if existing_vote:
                    flash('You have already voted for this option.', 'error')
                else:
                    # Check if the citizen exists
                    cur.execute("SELECT * FROM citizens WHERE citizen_id = ?", (citizen_id,))
                    citizen = cur.fetchone()

                    if citizen:
                        cur.execute("INSERT INTO votes (vote_id, citizen_id, date) VALUES (?, ?, ?)",
                                    (vote_id, citizen_id, current_time))
                        conn.commit()
                        flash('Vote submitted successfully!', 'success')
                    else:
                        flash('Citizen ID not found, please try again.', 'error')
        except Exception as e:
            flash(f'Error submitting vote: {e}', 'error')

    # Pass the vote_id to the vote.html template
    vote_id = request.form.get('vote_id') or request.args.get('vote_id')
    return render_template("vote.html", vote_id=vote_id)

    # Pass the vote_id to the vote.html template
    vote_id = request.form.get('vote_id') or request.args.get('vote_id')
    return render_template("vote.html", vote_id=vote_id)

    # Pass the vote_id to the vote.html template
    vote_id = request.form.get('vote_id') or request.args.get('vote_id')
    return render_template("vote.html", vote_id=vote_id)


    # Pass the vote_id to the vote.html template
    vote_id = request.args.get('vote_id')
    return render_template("vote.html", vote_id=vote_id)

# Route to list all votes
@app.route("/list_votes")
def list_votes():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM votes")
    rows = cur.fetchall()
    con.close()
    return render_template("list_votes.html", rows=rows)

# Route to delete a vote
@app.route("/delete_vote", methods=['POST'])
def delete_vote():
    if request.method == 'POST':
        try:
            vote_id = request.form['vote_id']
            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM votes WHERE vote_id = ?", (vote_id,))
                con.commit()
                msg = "Vote successfully deleted"
        except Exception as e:
            con.rollback()
            msg = f"Error in vote delete operation: {e}"
        finally:
            con.close()
            flash(msg)
            return redirect(url_for('list_votes'))

if __name__ == "__main__":
    app.run(debug=True,port=3000)

