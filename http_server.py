import json
from socketserver import ThreadingTCPServer
from http.server import SimpleHTTPRequestHandler
from serve_static_files import serve_statics
from settings import SERVER_HOST, SERVER_PORT, STATIC_DIR
from endpoints import (
    handle_signup, handle_login, handle_get_rooms, handle_chat_room,
    handle_create_room, handle_create_message, handle_join_room,
    handle_get_online_users
)


class RequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_GET(self):
        # Serve static files
        if serve_statics(self):
            return

        # Map paths to corresponding HTML files
        path_mappings = {
            '/': 'index.html',
            '/signup': 'signup.html',
            '/login': 'login.html',
            '/rooms': 'rooms.html',
            '/create-room': 'create-room.html'
        }

        # Handle special cases
        for path, file_name in path_mappings.items():
            if self.path == path:
                self.path = file_name
                break
        else:
            # Handle chat-related paths
            if self.path.startswith('/chat'):
                room_name = self.path[:-1].split('/')[-1]
                self.path = 'chat.html'
                room_data, _ = handle_chat_room(room_name)
                if room_data is None:
                    self.send_error(404, "Chat data not found")
                    return
            elif self.path == '/get-rooms':
                rooms_json = handle_get_rooms()
                self.send_response_and_data(200, 'application/json', rooms_json)
                return
            elif self.path.startswith('/get-room-messages'):
                query_string = self.path.split('?')[1]
                room_name = query_string.split('=')[1]
                room_data, room_messages = handle_chat_room(room_name)
                if room_data is None:
                    self.send_error(404, "Chat data not found")
                    return
                else:
                    self.send_response_and_data(200, 'application/json', room_messages)
                    return
            elif self.path.startswith('/get-online-users'):
                query_string = self.path.split('?')[1]
                room_name = query_string.split('=')[1]
                online_users = handle_get_online_users(room_name)
                self.send_response_and_data(200, 'application/json', online_users)
                return

        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        # Process the received data as needed
        endpoint_mappings = {
            '/signup': handle_signup,
            '/login': handle_login,
            '/create-room': handle_create_room,
            '/create-message': handle_create_message
        }

        for path, handler in endpoint_mappings.items():
            if self.path == path:
                handler(data)
                break
        else:
            # Handle '/join' path
            if self.path.startswith('/join'):
                query_string = self.path.split('?')[1]
                room_name = query_string.split('=')[1]
                self.path = 'chat.html'
                handle_join_room(room_name, data['authToken'])

        self.send_response_and_data(200, 'application/json', {'status': 'success'})

    def send_response_and_data(self, status, content_type, data):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))


httpd = ThreadingTCPServer((SERVER_HOST, SERVER_PORT), RequestHandler)

# Keep the server running
try:
    print("Server running on port 8000")
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
