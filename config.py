import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/student-management-record")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
