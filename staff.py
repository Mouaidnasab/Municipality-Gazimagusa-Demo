from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__, template_folder='templates_staff')
app.secret_key = 'supersecretkey'
port = 4000

# Database setup
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home Page route
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/blog")
def blog():
    return render_template("home.html")
    

@app.route("/add_news", methods=['POST', 'GET'])
def add_news():
    if request.method == 'POST':
        try:
            title = request.form['title']
            body = request.form['body']
            current_time = datetime.now().strftime("%Y-%m-%d")

            with get_db_connection() as con:
                cur = con.cursor()

                cur.execute("INSERT INTO news (body, title, date_added) VALUES (?, ?, ?)",
                            (body, title, current_time))
                con.commit()
                print(f"DEBUG: Inserted {body}, {title}, {current_time} into skill_sharing table")

        except Exception as e:
            con.rollback()
            print(f"DEBUG: Error in insert operation: {e}")
    return render_template("add_news.html")


# Route to list all news
@app.route("/news")
def news():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM news")
    rows = cur.fetchall()
    con.close()
    print(f"DEBUG: Retrieved rows: {rows}")
    return render_template("list_news.html", rows=rows)

# Route to delete a news
@app.route("/delete_news", methods=['POST'])
def delete_news():
    if request.method == 'POST':
        try:
            news_id = request.form['id']
            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM news WHERE news_id = ?", (news_id,))
                con.commit()
                msg = "Record successfully deleted"
        except Exception as e:
            con.rollback()
            msg = f"Error in delete operation: {e}"

        finally:
            con.close()
            flash(msg)
            return redirect(url_for('news'))



# Route to list all skill sharing
@app.route("/skill_sharing")
def skill_sharing():
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM skill_sharing")
    rows = cur.fetchall()
    con.close()
    print(f"DEBUG: Retrieved rows: {rows}")
    return render_template("list_ss.html", rows=rows)


# Route to delete a skill Sharing
@app.route("/delete_ss", methods=['POST'])
def delete_ss():
    if request.method == 'POST':
        try:
            ss_id = request.form['id']
            with get_db_connection() as con:
                cur = con.cursor()
                cur.execute("DELETE FROM skill_sharing WHERE ss_id = ?", (ss_id,))
                con.commit()
                msg = "Record successfully deleted"
        except Exception as e:
            con.rollback()
            msg = f"Error in delete operation: {e}"

        finally:
            con.close()
            flash(msg)
            return redirect(url_for('skill_sharing'))




if __name__ == "__main__":
    app.run(debug=True,port=4000)

