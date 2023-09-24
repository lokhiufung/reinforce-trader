from fastapi import APIRouter, Depends, Request
from pymongo import MongoClient

from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api import config


# Create the APIRouter instance
strategies_router = APIRouter(
    prefix='/strategies',
    tags=['strategies'],
)

@strategies_router.get('/', status_code=200)
def get_strategies(db_client: MongoClient = Depends(get_db_client)):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    strategies = trades_collection.distinct('strategy')
    return strategies


# trade analytics
@strategies_router.get("/{strategy}/winrate")
async def get_winrate(request: Request, strategy: str, ticker: str=None, db_client: MongoClient = Depends(get_db_client)):
    
    match_filter = {
        "strategy": strategy,
        "outcome": { "$in": ["Win", "Loss"] }
    }
    if ticker:
        match_filter["ticker"] = ticker

    pipeline = [
        {
            "$match": match_filter,
        },
        {
        "$group": {
            "_id": None,
            "totalTrades": { "$sum": 1 },
            "winningTrades": {
            "$sum": {
                "$cond": [{ "$eq": ["$outcome", "Win"] }, 1, 0]
            }
            }
        }
        },
        {
        "$project": {
            "winRate": {
            "$multiply": [
                { "$divide": ["$winningTrades", "$totalTrades"] },
                100
            ]
            }
        }
        }
    ]
    result = db_client[config.DB_NAME]['trade'].aggregate(pipeline)
    winrate = result[0] if result else None
    return winrate


@strategies_router.get("/{strategy}/profit_loss")
async def get_profit_loss(request: Request, strategy: str, ticker: str=None, db_client: MongoClient = Depends(get_db_client)):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    
    match_filter = {"strategy": strategy}
    if ticker:
        match_filter["ticker"] = ticker

    pipeline = [
        {
            "$match": match_filter,
        },
        {
            "$group": {
                "_id": None,
                "totalProfitLoss": { "$sum": "$profit" }  # Assuming 'profit' is a field in your trades collection
            }
        }
    ]
    
    result = trades_collection.aggregate(pipeline)
    profit_loss = result[0] if result else None  # Retrieve the first item from the result, if available
    return profit_loss