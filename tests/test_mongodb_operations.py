import unittest
from models import User, Room, Message
from mongodb_operations import MongoDBOperations
from settings import DB_NAME, SALT, MONGO_URI


class TestMongoDBOperations(unittest.TestCase):
    def setUp(self):
        self.DB_NAME = 'TESTING_DB'
        self.db_operations = MongoDBOperations(MONGO_URI, self.DB_NAME)
        self.user = User('user1', 'password')
        self.room = Room('General Room')
        self.message_content = 'Hello, World!'

    def tearDown(self):
        # drop the database after each test
        self.db_operations.client.drop_database(self.DB_NAME)
        pass

    def test_create_user(self):
        created_user = self.db_operations.create_user(self.user)
        self.assertIsNotNone(created_user)
        retrieved_user = self.db_operations.get_user_by_id(created_user['_id'])
        self.assertEqual(retrieved_user['username'], self.user.username)

    def test_authenticate_user(self):
        created_user = self.db_operations.create_user(self.user)
        authenticated_user = self.db_operations.authenticate_user(created_user['auth_token'])
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user['username'], self.user.username)

    def test_create_room(self):
        room_id = self.db_operations.create_room(self.room)
        self.assertIsNotNone(room_id)
        retrieved_room = self.db_operations.get_room_by_id(room_id)
        self.assertEqual(retrieved_room.name, self.room.name)

    def test_create_message(self):
        created_user = self.db_operations.create_user(self.user)
        room_id = self.db_operations.create_room(self.room)
        message = Message(self.message_content, created_user['_id'], room_id)
        message_id = self.db_operations.create_message(message)
        self.assertIsNotNone(message_id)
        retrieved_message = self.db_operations.get_message_by_id(message_id)
        self.assertEqual(retrieved_message.content, self.message_content)

    def test_add_remove_user_to_room(self):
        created_user = self.db_operations.create_user(self.user)
        room_id = self.db_operations.create_room(self.room)
        room = self.db_operations.add_user_to_room(created_user['_id'], self.room.name)
        self.assertIn(created_user['_id'], room.users)

        room = self.db_operations.remove_user_from_room(created_user['_id'], self.room.name)
        self.assertNotIn(created_user['_id'], room.users)


if __name__ == '__main__':
    unittest.main()
