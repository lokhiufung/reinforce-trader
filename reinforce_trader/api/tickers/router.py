from fastapi import APIRouter, Depends
from pymongo import MongoClient

from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api import config


# Create the APIRouter instance
tickers_router = APIRouter(
    prefix='/tickers',
    tags=['tickers'],
)

@tickers_router.get('/', status_code=200)
def get_tickers(db_client: MongoClient = Depends(get_db_client)):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    tickers = trades_collection.distinct('ticker')
    return tickers

