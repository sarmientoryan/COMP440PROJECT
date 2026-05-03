import bcrypt
import random
from faker import Faker
import mysql.connector
from datetime import date

fake = Faker()

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Woodwindow8@",
    database="project_db"
)

cursor = db.cursor()

NUM_USERS = 50
FEATURES = ["Wi-Fi", "Kitchen", "Mountainview", "Pool", "Parking"]

usernames = []
rental_map = {}  

today = date.today()

for i in range(NUM_USERS):
    username = f"user{i}"
    password = bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode()

    try:
        cursor.execute("""
            INSERT INTO user (username, password, firstName, lastName, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            username,
            password,
            fake.first_name(),
            fake.last_name(),
            f"user{i}@test.com",
            f"555000{i:04d}"
        ))
        usernames.append(username)
    except:
        # skip duplicates if re-run
        continue

db.commit()

#RENTALS
descriptions ={ 
    "Wi-Fi": [
        "High-speed Wi-Fi is available throughout the property.",
        "Fast and reliable internet for work or streaming.",
        "Strong Wi-Fi connection in all rooms.",
        "Stay connected with free high-speed Wi-Fi."],

    "Kitchen": [
        "Fully equipped kitchen available for cooking meals.",
        "Modern kitchen with all essential appliances.",
        "Guests can enjoy a clean, functional kitchen space.",
        "Spacious kitchen ideal for home-cooked meals."
        ],

    "Mountainview" :
        ["Beautiful mountain views from the balcony.",
        "Scenic surroundings with a peaceful mountain view.",
        "Enjoy breathtaking views of nearby mountains.",
        "Relax with a stunning natural mountain backdrop."
        ],

    "Pool":
        ["Access to a clean and well-maintained pool.",
        "Relax by the refreshing on-site swimming pool.",
        "Outdoor pool available for guest use.",
        "Enjoy a private-style pool experience during your stay."
        ],

    "Parking":
        [ "Free parking available on-site for guests.",
        "Convenient and secure parking included.",
        "Ample parking space available for all visitors.",
        "Easy access parking right next to the property."
        ]
 }


for username in usernames:
    rental_map[username] = []

    for _ in range(2):  # max allowed per day
    
        features_used = random.sample(FEATURES, k=random.randint(2, 3))
        # pick ONE feature to generate description from
        primary_feature = random.choice(features_used)
        description = random.choice(descriptions[primary_feature])

        cursor.execute("""
            INSERT INTO rental_unit (username, title, description, price, post_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            username,
            fake.city(),
            description,
            random.randint(50, 300),
            today
        ))

        rental_id = cursor.lastrowid
        rental_map[username].append(rental_id)

        # add 2–3 features per rental
        for feat in features_used:
            cursor.execute("""
                INSERT INTO feature (rental_id, feature)
                VALUES (%s, %s)
            """, (rental_id, feat))

db.commit()

#REVIEWS 
reviews = {
    "poor": [
        "The place was dirty and not well maintained.",
        "Very disappointing stay, would not recommend.",
        "Facilities were broken and the host was unresponsive.",
        "Not worth the price at all."
    ],
    "fair": [
        "The stay was okay but had several issues.",
        "Average experience, nothing special.",
        "Some amenities worked, others didn’t.",
        "Decent for a short stay but could be better."
    ],
    "good": [
        "Nice place overall, had a pleasant stay.",
        "Everything was as expected and comfortable.",
        "Good value for the price.",
        "Clean and convenient location."
    ],
    "excellent": [
        "Amazing stay, everything was perfect!",
        "Absolutely loved this place, highly recommend.",
        "Great host and excellent amenities.",
        "One of the best places I’ve stayed at."
    ]
}

all_rentals = []
for rlist in rental_map.values():
    all_rentals.extend(rlist)

for username in usernames:
    reviewed = set()

    # rentals NOT owned by this user
    other_rentals = [
        r for r in all_rentals if r not in rental_map[username]
    ]

    for _ in range(2):  # <= 3/day, we use 2
        rental_id = random.choice(other_rentals)

        # no duplicate review
        while rental_id in reviewed:
            rental_id = random.choice(other_rentals)

        reviewed.add(rental_id)

        score = random.choice(["excellent", "good", "fair", "poor"])
        remark = random.choice(reviews[score])

        cursor.execute("""
            INSERT INTO review (rental_id, username, score, remark, review_date)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            rental_id,
            username,
            score,
            remark,
            today
        ))

db.commit()

print("Seeding complete.")