import pymongo

from mongodb_operations import MongoDBOperations
from dotenv import load_dotenv
import os

load_dotenv()

# MongoDB configuration
CACHE_MONGO_URI = os.getenv("CACHE_MONGO_URI")
CACHE_DB_NAME = os.getenv("CACHE_DB_NAME")


class CachedDatabase:
    def __init__(self, uri, db_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]
        self.active_connections = {}  # { "room_name": [{"username": "user1", "websocket": websocket1}, ...] }

    def add_connection(self, room_name, username, websocket):
        # save the connection to the database
        self.db.active_connections.insert_one({"room_name": room_name, "username": username})

    def remove_connection(self, room_name, websocket):
        # remove the connection from the database
        self.db.active_connections.delete_one({"room_name": room_name, "websocket": websocket})


# Instantiate CustomDatabase
custom_db = CachedDatabase()
