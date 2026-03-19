from flask import Flask, request, redirect, render_template
import mysql.connector
import bcrypt


app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
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
        return "Passwords do not match"

    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM user WHERE username=%s OR email=%s OR phone=%s",
        (username, email, phone)
    )

    if cursor.fetchone():
        return "Duplicate username/email/phone"

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cursor.execute("""
        INSERT INTO user (username, password, firstName, lastName, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (username, hashed, first, last, email, phone))

    db.commit()

    return "Signup successful"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor = db.cursor()
    cursor.execute("SELECT password FROM user WHERE username=%s", (username,))
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password.encode(), result[0].encode()):
        return "Login successful"
    else:
        return "Invalid credentials"
    
cursor = db.cursor()
cursor.execute("SHOW TABLES")
for table in cursor:
    print(table)

if __name__ == '__main__':
    app.run(debug=True)