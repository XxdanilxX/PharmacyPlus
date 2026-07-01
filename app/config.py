import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "pharmacy2024-dev")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.environ.get("MONGO_DB", "pharmacy_db")
    USE_MOCK_DB = os.environ.get("USE_MOCK_DB", "0") == "1"
    PORT = int(os.environ.get("PORT", 5000))
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "1") == "1"
