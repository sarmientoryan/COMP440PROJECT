step 1: run 
pip install -r requirements.txt

step 2: run this in MySQL Workbench:

CREATE DATABASE project_db;
USE project_db;

-- Phase 1
CREATE TABLE user (
    username  VARCHAR(50)  PRIMARY KEY,
    password  VARCHAR(255) NOT NULL,
    firstName VARCHAR(50),
    lastName  VARCHAR(50),
    email     VARCHAR(100) UNIQUE,
    phone     VARCHAR(20)  UNIQUE
);

-- Phase 2
CREATE TABLE rental_unit (
    rental_id   INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50)    NOT NULL,
    title       VARCHAR(200)   NOT NULL,
    description TEXT,
    price       DECIMAL(10,2)  NOT NULL,
    post_date   DATE           NOT NULL,
    FOREIGN KEY (username) REFERENCES user(username)
);

CREATE TABLE feature (
    rental_id INT          NOT NULL,
    feature   VARCHAR(50)  NOT NULL,
    PRIMARY KEY (rental_id, feature),
    FOREIGN KEY (rental_id) REFERENCES rental_unit(rental_id)
);

CREATE TABLE review (
    review_id   INT AUTO_INCREMENT PRIMARY KEY,
    rental_id   INT          NOT NULL,
    username    VARCHAR(50)  NOT NULL,
    score       ENUM('Excellent', 'Good', 'Fair', 'Poor') NOT NULL,
    remark      TEXT,
    review_date DATE         NOT NULL,
    UNIQUE KEY one_review_per_user (rental_id, username),
    FOREIGN KEY (rental_id) REFERENCES rental_unit(rental_id),
    FOREIGN KEY (username)  REFERENCES user(username)
);

step 3: change the password in app.py to match your MySQL password
(the line says password="YOUR_MYSQL_PASSWORD")

step 4: run
python app.py

phase 2 youtube link: https://www.youtube.com/watch?v=dda-1LYWCAc


PHASE 3 

run pip install -r requirements.txt to download Faker
then run python script.py to add in users
then run python app.py 

***if you want to delete all reviews and fake users***
DELETE FROM review WHERE review_id >= 0;
DELETE FROM feature WHERE rental_id >= 0;
DELETE FROM rental_unit WHERE rental_id >= 0;
DELETE FROM user
WHERE username LIKE 'user%';
