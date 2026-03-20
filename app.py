from flask import Flask, request, redirect, render_template, session
import mysql.connector
import bcrypt


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


   