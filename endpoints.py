import json

from models import User, Room, Message
from mongodb_operations import db_operations


def handle_signup(data):
    # Create a user object
    user = User(data["username"], data["password"])
    # Insert user into MongoDB
    user = db_operations.create_user(user)
    return user


def handle_login(data):
    # Authenticate user based on username and password
    auth_token = db_operations.get_auth_token(data["username"], data["password"])
    return auth_token['auth_token']


def handle_create_room(data):
    # Create a room object
    room = Room(data["roomName"])

    # Insert room into MongoDB
    db_operations.create_room(room)


def handle_get_rooms():
    # Assuming db_operations.get_rooms() returns a list of MongoDB documents
    rooms_data = db_operations.get_rooms()

    # Assuming Room.from_mongo() converts MongoDB documents into Room instances
    print('rooms_data', rooms_data)
    rooms = [Room.from_mongo(room_data) for room_data in rooms_data]

    # Assuming Room.to_dict() returns a dictionary representation of a Room instance
    rooms_as_dicts = [room.to_dict() for room in rooms]

    return json.dumps({"rooms": rooms_as_dicts})


def handle_chat_room(room_name):
    # Retrieve chat data based on the room name and serve the chat HTML
    room_data = db_operations.get_room_by_name(room_name)
    room_messages = db_operations.get_room_messages(room_name)
    room_messages = [Message.from_mongo(message) for message in room_messages]
    room_messages = [message.to_dict() for message in room_messages]

    # get the message sender's username
    for message in room_messages:
        sender = db_operations.get_user_by_id(message["sender_id"])
        message["sender"] = sender["username"]
        del message["sender_id"]

    print(room_messages)

    room_messages = json.dumps({"messages": room_messages})

    return room_data, room_messages
    # if chat_data is not None:
    #     # You might need to modify the HTML file or use a template engine to inject the chat data into the HTML
    #     # Example: Replace a placeholder in chat.html with the actual chat data
    #     # chat_html = read_chat_html_file_and_replace_placeholder(chat_data)
    #     # self.wfile.write(chat_html.encode())
    # else:
    #     # Handle the case where chat data for the specified room_name is not available
    #     self.send_error(404, "Chat data not found")


def handle_create_message(data):
    # Create a message object
    message = Message(data["content"], data["sender_id"], data["room_name"])

    # Insert message into MongoDB
    db_operations.create_message(message)


def handle_join_room(room_name, auth_token):
    # Authenticate user based on authToken
    user = db_operations.authenticate_user(auth_token)
    db_operations.add_user_to_room(user['_id'], room_name)

    return True


def handle_get_online_users(room_name):
    # Retrieve online users based on the room name
    room = db_operations.get_room_by_name(room_name)

    users = []
    for user_id in room.users:
        user = db_operations.get_user_by_id(user_id)
        users.append({
            'username': user['username'],
        })

    return json.dumps({"onlineUsers": users})
