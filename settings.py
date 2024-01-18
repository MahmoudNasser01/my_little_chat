
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
MONGO_USERNAME = os.getenv("MONGO_USERNAME")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

SALT = SECRET_KEY.encode()


# server configuration
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'frontend')

# WebSocket server configuration
WS_HOST = os.getenv("WS_HOST")
WS_PORT = int(os.getenv("WS_PORT"))
