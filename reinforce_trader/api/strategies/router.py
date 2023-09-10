from fastapi import APIRouter, Depends
from pymongo import MongoClient

from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api import config


# Create the APIRouter instance
strategies_router = APIRouter(
    prefix='/strategies',
    tags=['strategies'],
)

@strategies_router.get('/', status_code=200)
def get_tickers(db_client: MongoClient = Depends(get_db_client)):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    strategies = trades_collection.distinct('strategy')
    return strategies

