import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from bson.json_util import dumps

# Load environment variables
load_dotenv()

# Environment variable setup
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))  # Default port is 27017

# Utility functions
def mongo_connect():
    """Create a MongoClient connection."""
    try:
        client = MongoClient(
            f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}"
        )
        return client.db  # Return the specific database
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

def mongo_home_by_id(home_id):
    db = mongo_connect()
    try:
        home = db.homes.find({"home_id": home_id}).limit(1)
        if home:
            return dumps(home)
        return None
    except Exception as e:
        logging.error(f"Error fetching room by ID: {e}")
        return None
    
def mongo_insert_user(user_data):
    db = mongo_connect()
    try:
        db.homes.update_one(
                            {'home_id': user_data['home_id']},
                            {'$addToSet': {'family': user_data['user_id']}}
                        )
        logging.info("User data inserted successfully")
    except Exception as e:
        logging.error(f"Error inserting user data: {e}")

def mongo_insert_home(home_data):
    db = mongo_connect()
    try:
        db.homes.insert_one(home_data)
        logging.info("Home data inserted successfully")
    except Exception as e:
        logging.error(f"Error inserting home data: {e}")

def mongo_find_user(user_id):
    db = mongo_connect()
    try:
        user = db.homes.find({'family': user_id})
        if user:
            return dumps(user)
        return None
    except Exception as e:
        logging.error(f"Error fetching user command: {e}")
        return None