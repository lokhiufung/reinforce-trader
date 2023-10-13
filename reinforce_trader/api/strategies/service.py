from bson import ObjectId

from fastapi import HTTPException

from reinforce_trader.api.strategies.models.strategy import Strategy
from reinforce_trader.api import config


def create_strategy(
    user_id: str,
    strategy: Strategy,
    db_client,
):
    # Get the database and collection
    db = db_client[config.DB_NAME]
    strategies_collection = db["strategies"]
    # Check if strategy name already exists
    if strategies_collection.find_one({"name": strategy.name, "userId": user_id}):
        raise HTTPException(
            status_code=400,
            detail=f"Strategy with this name already exists with userId={user_id}",
        )
    
    # Insert the new strategy into the database
    strategy_dict = strategy.model_dump()
    # add userId and initialCash to the strategy_dict
    strategy_dict['userId'] = user_id
    # set cash as initial cash
    strategy_dict['cash'] = strategy.initialCash

    inserted_strategy = strategies_collection.insert_one(strategy_dict)
    strategy_dict['_id'] = str(inserted_strategy.inserted_id)
    return {
        "_id": strategy_dict['_id'],
    }


def get_strategies(user_id, db_client):
    db = db_client[config.DB_NAME]
    strategies_collection = db["strategies"]
    query = {"userId": user_id}
    strategies = list(strategies_collection.find(query))
    for strategy in strategies:
        strategy['_id'] = str(strategy['_id'])
    return strategies


def get_strategy(user_id: str, strategy_id: str, db_client):
    db = db_client[config.DB_NAME]
    strategies_collection = db["strategies"]

    strategy = strategies_collection.find_one({"_id": ObjectId(strategy_id), "userId": user_id})
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    strategy['_id'] = str(strategy['_id'])
    return strategy


def update_strategy(
        user_id: str,
        strategy_id: str, 
        name,
        initial_cash,
        db_client,
    ):
    db = db_client[config.DB_NAME]
    strategies_collection = db["strategies"]
    
    # Check if strategy name already exists
    if not strategies_collection.find_one({"_id": ObjectId(strategy_id), 'userId': user_id}):
        raise HTTPException(
            status_code=404,
            detail=f"Strategy with this name does not exist with userId={user_id}",
        )
    
    # Create an update object with only the provided fields
    update_data = {}

    if name is not None:
        update_data["name"] = name

    if initial_cash is not None:
        update_data["initialCash"] = initial_cash

    # if cash is not None:
    #     update_data["cash"] = cash
    
    # Update the strategy
    strategies_collection.update_one({"_id": ObjectId(strategy_id), "userId": user_id}, {"$set": update_data})
    return {
        '_id': strategy_id,
    }


def delete_strategy(
        user_id: str,
        strategy_id: str,
        db_client,
    ):
    db = db_client[config.DB_NAME]
    strategies_collection = db["strategies"]
    
    # Delete the strategy
    deleted_strategy = strategies_collection.find_one_and_delete({"_id": ObjectId(strategy_id), "userId": user_id})
    
    if not deleted_strategy:
        raise HTTPException(status_code=404, detail="Trade not found")
    deleted_strategy["_id"] = str(deleted_strategy["_id"])  # Convert ObjectId to str
    return {
        "_id": deleted_strategy["_id"]
    }


def get_winrate(strategy_id, ticker, db_client):
    match_filter = {
        "_id": ObjectId(strategy_id),
        "label": { "$in": ["win", "loss"] }
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


def get_pnl(strategy_id, ticker, db_client):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]
    
    match_filter = {"strategy": ObjectId(strategy_id)}
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