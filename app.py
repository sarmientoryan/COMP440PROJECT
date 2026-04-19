from flask import Flask, request, redirect, render_template, session
import mysql.connector
import bcrypt
from datetime import date


app = Flask(__name__)
app.secret_key = "cool_key"

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Woodwindow8@",
    database="project_db"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form

    username = data['username']
    password = data['password']
    confirm = data['confirm']
    email = data['email']
    phone = data['phone']
    first = data['firstName']
    last = data['lastName']

    if password != confirm:
        return render_template('index.html', msg="Passwords do not match")

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM user WHERE username=%s OR email=%s OR phone=%s",
        (username, email, phone)
    )

    if cursor.fetchone():
        return render_template('index.html', msg="Duplicate username/email/phone")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO user (username, password, firstName, lastName, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, hashed, first, last, email, phone))

    db.commit()
    return render_template('index.html', msg="Signup Successful")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("SELECT password FROM user WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        session["username"] = username
        return render_template('loggedin.html')
    else:
        return render_template('index.html', inv_msg="Invalid credentials")

# ── Phase 2 ──────────────────────────────────────────────────────────────────

@app.route('/post_rental', methods=['POST'])
def post_rental():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    title = request.form['title']
    description = request.form['description']
    price = request.form['price']
    features_raw = request.form['features']
    today = date.today()

    cursor = db.cursor()

    # Max 2 rental units per day
    cursor.execute(
        "SELECT COUNT(*) FROM rental_unit WHERE username=%s AND post_date=%s",
        (username, today)
    )
    if cursor.fetchone()[0] >= 2:
        return render_template('loggedin.html', rental_msg="You can only post 2 rental units per day.")

    cursor.execute(
        "INSERT INTO rental_unit (username, title, description, price, post_date) VALUES (%s, %s, %s, %s, %s)",
        (username, title, description, price, today)
    )
    db.commit()
    rental_id = cursor.lastrowid

    for feat in features_raw.split(','):
        feat = feat.strip()
        if feat:
            cursor.execute(
                "INSERT INTO feature (rental_id, feature) VALUES (%s, %s)",
                (rental_id, feat)
            )
    db.commit()

    return render_template('loggedin.html', rental_msg="Rental unit posted successfully!")


@app.route('/search', methods=['GET'])
def search():
    if 'username' not in session:
        return redirect('/')

    feature = request.args.get('feature', '').strip()
    results = []

    if feature:
        cursor = db.cursor()
        cursor.execute("""
            SELECT r.rental_id, r.title, r.description, r.price, r.username,
                   GROUP_CONCAT(f.feature SEPARATOR ', ') AS features
            FROM rental_unit r
            JOIN feature f ON r.rental_id = f.rental_id
            WHERE r.rental_id IN (
                SELECT rental_id FROM feature WHERE feature = %s
            )
            GROUP BY r.rental_id
        """, (feature,))
        results = cursor.fetchall()

    return render_template('loggedin.html', results=results, searched_feature=feature)


@app.route('/post_review', methods=['POST'])
def post_review():
    if 'username' not in session:
        return redirect('/')

    username = session['username']
    rental_id = request.form['rental_id']
    score = request.form['score']
    remark = request.form['remark']
    last_feature = request.form.get('last_feature', '').strip()
    today = date.today()

    cursor = db.cursor()

    # No self-review
    cursor.execute("SELECT username FROM rental_unit WHERE rental_id=%s", (rental_id,))
    owner = cursor.fetchone()
    if owner and owner[0] == username:
        return render_template('loggedin.html',
                               review_msg="You cannot review your own rental unit.",
                               searched_feature=last_feature)

    # One review per rental unit per user
    cursor.execute(
        "SELECT * FROM review WHERE rental_id=%s AND username=%s",
        (rental_id, username)
    )
    if cursor.fetchone():
        return render_template('loggedin.html',
                               review_msg="You have already reviewed this rental unit.",
                               searched_feature=last_feature)

    # Max 3 reviews per day
    cursor.execute(
        "SELECT COUNT(*) FROM review WHERE username=%s AND review_date=%s",
        (username, today)
    )
    if cursor.fetchone()[0] >= 3:
        return render_template('loggedin.html',
                               review_msg="You can only post 3 reviews per day.",
                               searched_feature=last_feature)

    cursor.execute(
        "INSERT INTO review (rental_id, username, score, remark, review_date) VALUES (%s, %s, %s, %s, %s)",
        (rental_id, username, score, remark, today)
    )
    db.commit()

    # Re-run the search so the results table is preserved after submitting
    results = []
    if last_feature:
        cursor.execute("""
            SELECT r.rental_id, r.title, r.description, r.price, r.username,
                   GROUP_CONCAT(f.feature SEPARATOR ', ') AS features
            FROM rental_unit r
            JOIN feature f ON r.rental_id = f.rental_id
            WHERE r.rental_id IN (
                SELECT rental_id FROM feature WHERE feature = %s
            )
            GROUP BY r.rental_id
        """, (last_feature,))
        results = cursor.fetchall()

    return render_template('loggedin.html',
                           review_msg="Review submitted successfully!",
                           results=results,
                           searched_feature=last_feature)

# ─────────────────────────────────────────────────────────────────────────────

cursor = db.cursor()
cursor.execute("SHOW TABLES")
for table in cursor:
    print(table)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
