import hashlib
import os

import pymongo
from bson import ObjectId
from models import Room, User, Message
from settings import DB_NAME, SALT, MONGO_URI


def hash_password(password):
    salted_password = password.encode() + SALT
    return hashlib.sha256(salted_password).hexdigest()


class MongoDBOperations:
    def __init__(self, uri, db_name):
        self.client = pymongo.MongoClient(uri)
        self.db = self.client[db_name]

    def _get_user_data(self, user):
        return {
            "username": user.username,
            "password_hash": hash_password(user.password),
            "auth_token": user.auth_token
        }

    def get_user_by_id(self, user_id):
        return self.db.users.find_one({"_id": ObjectId(user_id)})

    def create_user(self, user):
        user_data = self._get_user_data(user)
        try:
            result = self.db.users.insert_one(user_data)
            return self.get_user_by_id(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def authenticate_user(self, auth_token):
        return self.db.users.find_one({"auth_token": auth_token})

    def get_auth_token(self, username, password):
        hashed_password_input = hash_password(password)
        return self.db.users.find_one({"username": username, "password_hash": hashed_password_input})

    def _get_room_data(self, room):
        return {"name": room.name}

    def create_room(self, room):
        room_data = self._get_room_data(room)
        result = self.db.rooms.insert_one(room_data)
        return result.inserted_id

    def _get_message_data(self, message):
        return {"content": message.content, "sender_id": message.sender_id, "room_name": message.room_name}

    def create_message(self, message):
        message_data = self._get_message_data(message)
        result = self.db.messages.insert_one(message_data)
        return result.inserted_id

    # Similar methods for Room and Message

    def _get_entity_by_id(self, collection, entity_id, entity_class):
        entity_data = self.db[collection].find_one({"_id": ObjectId(entity_id)})
        return entity_class.from_mongo(entity_data) if entity_data else None

    def get_room_by_id(self, room_id):
        return self._get_entity_by_id("rooms", room_id, Room)

    def get_room_by_name(self, room_name):
        room_data = self.db.rooms.find_one({"name": room_name})
        return Room.from_mongo(room_data) if room_data else None

    def get_message_by_id(self, message_id):
        return self._get_entity_by_id("messages", message_id, Message)

    def get_rooms(self):
        return self.db.rooms.find()

    def get_room_messages(self, room_name):
        return self.db.messages.find({"room_name": room_name})

    def _update_users_in_room(self, room_name, users):
        self.db.rooms.update_one({"name": room_name}, {"$set": {"users": users}})

    def add_user_to_room(self, user_id, room_name):
        room = self.get_room_by_name(room_name)
        if room and user_id not in room.users:
            room.users.append(user_id)
            self._update_users_in_room(room_name, room.users)
        return room

    def remove_user_from_room(self, user_id, room_name):
        room = self.get_room_by_name(room_name)
        if room and user_id in room.users:
            room.users.remove(user_id)
            self._update_users_in_room(room_name, room.users)
        return room


def run():
    uri = "mongodb://localhost:27017/"
    db_operations = MongoDBOperations(uri, DB_NAME)

    # Create a user
    user = User('user1', 'password')
    user = db_operations.create_user(user)
    print(f"Created user with ID: {user}")

    # Authenticate the user
    authenticated_user = db_operations.authenticate_user(user['auth_token'])
    print(f"Authenticated user: {authenticated_user}")

    # Retrieve user by ID
    retrieved_user = db_operations.get_user_by_id(user['_id'])
    print(f"Retrieved user: {retrieved_user}")

    # Create a room
    room = Room("General Room")
    room_id = db_operations.create_room(room)
    print(f"Created room with ID: {room_id}")

    # Create a message
    message = Message("Hello, World!", user['_id'], room_id)
    message_id = db_operations.create_message(message)
    print(f"Created message with ID: {message_id}")

    # Retrieve user by ID
    retrieved_user = db_operations.get_user_by_id(user['_id'])
    print(f"Retrieved user: {retrieved_user}")

    # Retrieve room by ID
    retrieved_room = db_operations.get_room_by_id(room_id)
    print(f"Retrieved room: {retrieved_room}")

    # Retrieve message by ID
    retrieved_message = db_operations.get_message_by_id(message_id)
    print(f"Retrieved message: {retrieved_message}")


if __name__ == "__main__":
    run()

# Instantiate MongoDBOperations
db_operations = MongoDBOperations(MONGO_URI, DB_NAME)
