import asyncio
import json
import os
import websockets
from dotenv import load_dotenv
from models import Message
from mongodb_operations import MongoDBOperations, db_operations
from settings import WS_HOST, WS_PORT

load_dotenv()

# Active WebSocket connections
active_connections = {}

# Maintain a mapping of user_id to WebSocket object
user_id_to_websocket = {}


async def handle_connection(websocket, path):
    try:
        while True:
            data = await websocket.recv()
            await process_received_data(data, websocket)
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed by the client: {e}")
    finally:
        await cleanup_connection(websocket)


async def process_received_data(data, websocket):
    loaded_data = json.loads(data)
    event = loaded_data.get('event', None)
    auth_token = loaded_data.get('auth_token', None)

    if auth_token:
        await handle_authenticated_user(loaded_data, auth_token, websocket)
    else:
        print("No auth_token provided.")


async def handle_authenticated_user(loaded_data, auth_token, websocket):
    user = db_operations.authenticate_user(auth_token)

    if user:
        room_name = loaded_data['room_name']
        connected_users = active_connections.get(room_name, [])
        user_id = str(user['_id'])

        connected_users.append({"user_id": user_id})
        active_connections[room_name] = connected_users
        user_id_to_websocket[user_id] = websocket

        if loaded_data['event'] == 'typing':
            await handle_typing_event(user, room_name)
        elif loaded_data['event'] == 'user-joined':
            await handle_user_joined_event(user, room_name)
        elif loaded_data['event'] == 'message':
            await handle_message_event(user, loaded_data)

    else:
        print("Authentication failed.")


async def handle_typing_event(user, room_name):
    message = {"event": "typing", "message": f"{user['username']} is typing..."}
    await broadcast(message, room_name, exclude_user_id=str(user['_id']))


async def handle_user_joined_event(user, room_name):
    message = {"event": "user-joined", "message": f"{user['username']} joined the chat"}
    await broadcast(message, room_name)


async def handle_message_event(user, loaded_data):
    message = Message(
        sender_id=user['_id'],
        room_name=loaded_data['room_name'],
        content=loaded_data['data']['content']
    )
    db_operations.create_message(message)

    server_message = {'event': 'message', 'message': 'a new message'}
    await broadcast(server_message, loaded_data['room_name'])


async def cleanup_connection(websocket):
    user_id = get_user_id_by_websocket(websocket)
    if user_id:
        for room_name, connected_users in active_connections.items():
            active_connections[room_name] = [
                user for user in connected_users if user.get('user_id') != user_id
            ]
        del user_id_to_websocket[user_id]
        print(user_id_to_websocket, active_connections)


async def broadcast(message, room_name, exclude_user_id=None):
    connected_users = active_connections.get(room_name, [])

    if exclude_user_id:
        connected_users = [user for user in connected_users if user['user_id'] != exclude_user_id]

    for connected_user in connected_users:
        user_id = connected_user['user_id']
        websocket = find_websocket_by_user_id(user_id)

        if websocket:
            await websocket.send(json.dumps(message))


def find_websocket_by_user_id(user_id):
    return user_id_to_websocket.get(str(user_id), None)


def get_user_id_by_websocket(websocket):
    for user_id, ws in user_id_to_websocket.items():
        if ws == websocket:
            return user_id
    return None


async def main():
    print(f"Starting WebSocket server at ws://{WS_HOST}:{WS_PORT}...")
    async with websockets.serve(handle_connection, WS_HOST, WS_PORT):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
