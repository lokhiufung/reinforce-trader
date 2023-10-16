from fastapi import APIRouter, Depends, Request
from pymongo import MongoClient

from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api import config


# Create the APIRouter instance
tickers_router = APIRouter(
    prefix='/users/{user_id}/tickers',
    tags=['tickers'],
)

@tickers_router.get('/', status_code=200)
def get_tickers(request: Request, user_id: str, strategy: str, db_client: MongoClient = Depends(get_db_client)):
    # e.g /users/user_id/tickers/?strategy=strategy_name
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    tickers = trades_collection.distinct('ticker', {'userId': user_id, 'strategy': strategy})  # use strategy name for query at this moment
    return tickers

