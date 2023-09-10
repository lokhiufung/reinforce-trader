
from pymongo import MongoClient

from reinforce_trader.api import config


def get_db_client() -> MongoClient:
    # Connect to MongoDB
    db_client = MongoClient(f"mongodb://{config.DB_USERNAME}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/")  # Update the connection string accordingly
    # db = client[DB_NAME]
    # trades_collection = db["trades"]
    return db_client
