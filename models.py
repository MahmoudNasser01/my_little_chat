import secrets
import hashlib
from bson import ObjectId


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.auth_token = secrets.token_urlsafe(32)

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            username=mongo_data["username"],
            password=mongo_data["password_hash"],
        )

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
        }


class Room:
    def __init__(self, name, users=None):
        self.name = name
        self.users = users if users else []

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            name=mongo_data["name"],
            users=mongo_data.get("users", [])
        )

    def to_dict(self):
        return {
            "name": self.name,
            "users": [str(user_id) for user_id in self.users]
        }


class Message:
    def __init__(self, content, sender_id, room_name):
        self.content = content
        self.sender_id = ObjectId(sender_id)
        self.room_name = room_name

    @classmethod
    def from_mongo(cls, mongo_data):
        return cls(
            content=mongo_data["content"],
            sender_id=str(mongo_data["sender_id"]),
            room_name=str(mongo_data["room_name"]),
        )

    def to_dict(self):
        return {
            "content": self.content,
            "sender_id": self.sender_id,
            "room_name": self.room_name
        }
