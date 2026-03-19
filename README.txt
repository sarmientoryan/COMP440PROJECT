step 1: run 
pip install -r requirements.txt

step2: run this in MYSQL Workbench:

CREATE DATABASE project_db;
USE project_db;

CREATE TABLE user (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(50),
    lastName VARCHAR(50),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20) UNIQUE
);

step 3: change the password in app.py to the password you use for MYSQL
says password="YOUR_MYSQL_PASSWORD"

you can then run 
python app.py