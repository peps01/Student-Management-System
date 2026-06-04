import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite")

# DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mongodb")

SQLITE_DB_PATH = os.path.join(BASE_DIR, "sms.db")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/sms")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
