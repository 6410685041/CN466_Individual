import os
from bson.json_util import dumps
from pymongo import MongoClient
import logging

from dotenv import load_dotenv
load_dotenv()

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))  # Default port is 27017

# Utility functions
def mongo_connect():
    try:
        client = MongoClient(host=MONGO_HOST, port=MONGO_PORT, username=MONGO_USER, password=MONGO_PASS)
        return client.db  # Return the specific database
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

def house_by_id(home_id):
    db = mongo_connect()
    try:
        home = db.houses.find({"home_id": home_id})[0]
        if home:
            return dumps(home)
        return None
    except Exception as e:
        logging.error(f"Error fetching house by ID: {e}")
        return None
    
def home_by_id(home_id):
    db = mongo_connect()
    try:
        home = db.homes.find({"home_id": home_id})[0]
        if home:
            return dumps(home)
        return None
    except Exception as e:
        logging.error(f"Error fetching home by ID: {e}")
        return None
    
def insert_house_data(doc):
    db = mongo_connect()
    try:
        db.houses.insert_one(doc)
        print("Insert Succesfully in database")
    except Exception as e:
        logging.error(f"Error insert new house data: {e}")

def insert_collected_data(collected_data):
    db = mongo_connect()
    try:
        db.houses.update_one(
                            {'home_id': collected_data['home_id']},
                            {'$push': {'collected': collected_data['collected'][0]}}
                        )
        print(f"Collected data is insert in {collected_data['home_id']} successfully")
    except Exception as e:
        logging.error(f"Error inserting collected data: {e}")