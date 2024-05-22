from flask import Flask, render_template, request, redirect, url_for, abort

app = Flask(__name__, template_folder='template')

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/map')
def map():
    return render_template("map.html")

@app.route('/online__tickets')
def online__tickets():
    return render_template("online__tickets.html")

@app.route('/blocked__cars')
def blocked__cars():
    return render_template("blocked__cars.html")

@app.route('/mayor')
def mayor():
    return render_template("mayor.html")

@app.route('/complaints')
def complaints():
    return render_template("complaints.html")


@app.route('/emergency')
def emergency():
    return render_template("emergency.html")

@app.route('/blog')
def blog():
    return render_template("blog.html")

@app.route('/transportation')
def transportation():
    return render_template("transportation.html")

@app.route('/skill__sharing')
def skill__sharing():
    return render_template("skill__sharing.html")

@app.route('/add_skill_sharing')
def add_skill_sharing():
    return render_template("add_skill_sharing.html")

@app.route('/digital__voting')
def digital__voting():
    return render_template("digital__voting.html")


@app.route('/online-tickets/bills')
def bills():
    return render_template("/online-tickets/bills.html")

@app.route('/online-tickets/can_request')
def can_request():
    return render_template("/online-tickets/can_request.html")

@app.route('/online-tickets/earthquake')
def earthquake():
    return render_template("/online-tickets/earthquake.html")

@app.route('/online-tickets/garbage')
def garbage():
    return render_template("/online-tickets/garbage.html")

@app.route('/online-tickets/reward_points')
def reward_points():
    return render_template("/online-tickets/reward_points.html")

@app.route('/online-tickets/sewege')
def sewege():
    return render_template("/online-tickets/sewege.html")

@app.route('/online-tickets/Spraying')
def Spraying():
    return render_template("/online-tickets/Spraying.html")

@app.route('/online-tickets/tree_pruning')
def tree_pruning():
    return render_template("/online-tickets/tree_pruning.html")


if __name__ == '__main__':
    app.run(debug=True, port=5000)
