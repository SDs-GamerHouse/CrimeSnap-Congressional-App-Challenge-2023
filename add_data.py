import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("private_database_key.json") # path/to/serviceAccountKey.json | You can get your service account key from the Firebase website
firebase_admin.initialize_app(cred,{
    "databaseURL": "https://crimiface-bcb44-default-rtdb.firebaseio.com/"
})

reference = db.reference("Criminals")

data = {
    "Joker": {
        "suspect": "Joker",
        "num_of_times_spotted": 0,
        "crime": "Murdering for pleasure",
        "last_spotted_on": "6/2/2023 00:54:34"
    },
    "Kylo Ren": {
        "suspect": "Kylo Ren",
        "num_of_times_spotted": 0,
        "crime": "Betrayal and Murder",
        "last_spotted_on": "6/2/2023 00:54:34"
    },
    "Loki": {
        "suspect": "Loki",
        "num_of_times_spotted": 0,
        "crime": "Genocide",
        "last_spotted_on": "6/2/2023 00:54:34" 
    },
    "The Mastermind": {
        "suspect": "The Mastermind",
        "num_of_times_spotted": 0,
        "crime": "Being too smart",
        "last_spotted_on": "6/2/2023 00:54:34"
    }

}

# Sending data to database
for key,value in data.items():
    reference.child(key).set(value)
