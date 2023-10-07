import os


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 27017)
DB_SCHEMA = os.getenv("DB_SCHEMA")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
FRONTEND_URL = os.getenv("FRONTEND_URL")
if DB_SCHEMA == "mongodb+srv":
    DB_URL = f'{DB_SCHEMA}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}'
else:
    DB_URL = f'{DB_SCHEMA}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}'
