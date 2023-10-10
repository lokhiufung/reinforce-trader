import base64
from datetime import datetime
from bson import ObjectId

from typing import List
from fastapi import APIRouter, HTTPException, Request, Depends
from pymongo import MongoClient

from reinforce_trader.api.trades.models.trade import Trade
from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api import config
from reinforce_trader.api.constants import * 


# Create the APIRouter instance
trades_router = APIRouter(
    prefix='/users/{user_id}/trades',
    tags=['trades'],
)

# create trade
@trades_router.post("/", status_code=201)
async def create_trade(
    user_id,
    trade: Trade,
    db_client: MongoClient = Depends(get_db_client)
): 
    db = db_client[config.DB_NAME]
    # check if the strategy exists first
    strategies_collection = db["strategies"]
    if not strategies_collection.find_one({"name": trade.strategy}):
        raise HTTPException(status_code=400, detail=f"Strategy '{trade.strategy}' not found. Please create a new strategy {trade.strategy} first.")
    trades_collection = db["trades"]

    trade_dict = trade.model_dump()
    # add user_id
    trade_dict['userId'] = user_id
    # Parse the string into a datetime object
    trade_dict['date'] = datetime.strptime(trade_dict['date'], DATE_FORMAT)
    
    inserted_trade = trades_collection.insert_one(trade_dict)
    trade_dict['_id'] = str(inserted_trade.inserted_id)
    trade_dict['date'] = datetime.strftime(trade_dict['date'], DATE_FORMAT)
    return {
        "_id": trade_dict['_id'],
    }


@trades_router.get("/")
async def get_trades(request: Request, user_id: str, strategy: str = None, ticker: str = None, db_client: MongoClient = Depends(get_db_client)):

    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]

    query = {
        "userId": user_id,
    }
    
    if strategy:
        query["strategy"] = strategy
    if ticker:
        query["ticker"] = ticker
    
    trades = list(trades_collection.find(query))
    for trade in trades:
        trade['_id'] = str(trade['_id'])
        trade['date'] = datetime.strftime(trade['date'], DATE_FORMAT)
        
        # # Check if 'image' field exists and convert it to base64 string
        # if 'image' in trade and trade['image'] is not None:
        #     trade['image'] = base64.b64encode(trade['image']).decode("utf-8")  # Convert binary data to base64 string
    return trades

@trades_router.get("/{trade_id}", response_model=Trade)
async def get_trade(user_id: str, trade_id: str, db_client: MongoClient = Depends(get_db_client)):

    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]

    trade = trades_collection.find_one({"_id": ObjectId(trade_id), "userId": user_id})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade['_id'] = str(trade['_id'])
    trade['date'] = datetime.strftime(trade['date'], DATE_FORMAT)
    # Check if 'image' field exists and convert it to base64 string
    # if 'image' in trade and trade['image'] is not None:
    #     trade['image'] = base64.b64encode(trade['image']).decode("utf-8")  # Convert binary data to base64 string
    return trade


@trades_router.put("/{trade_id}", response_model=None)
async def update_trade(
    user_id: str,
    trade_id: str,
    trade: Trade,
    db_client: MongoClient = Depends(get_db_client)
):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]

    existing_trade = trades_collection.find_one({"_id": ObjectId(trade_id), 'userId': user_id})
    if not existing_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    update_dict = {}
    if trade.strategy is not None:
        update_dict["strategy"] = trade.strategy
    if trade.ticker is not None:
        update_dict["ticker"] = trade.ticker
    if trade.price is not None:
        update_dict["price"] = trade.price
    if trade.date is not None:
        update_dict["date"] = datetime.strptime(trade.date, DATE_FORMAT)
    if trade.size is not None:
        update_dict["size"] = trade.size
    if trade.side is not None:
        update_dict["side"] = trade.side
    if trade.notes is not None:
        update_dict["notes"] = trade.notes

    trades_collection.update_one({"_id": ObjectId(trade_id)}, {'$set': update_dict})
    # trade['tradeDate'] = datetime.strftime(trade['tradeDate'], DATE_FORMAT)
    return {
        '_id': trade_id,
    }


@trades_router.delete("/{trade_id}", response_model=None, status_code=204)
async def delete_trade(user_id: str, trade_id: str, db_client: MongoClient = Depends(get_db_client)):
    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]

    deleted_trade = trades_collection.find_one_and_delete({"_id": ObjectId(trade_id), "user_id": user_id})
    if not deleted_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    deleted_trade["_id"] = str(deleted_trade["_id"])  # Convert ObjectId to str
    # deleted_trade['tradeDate'] = datetime.strftime(deleted_trade['tradeDate'], DATE_FORMAT)
    return {
        "_id": deleted_trade["_id"]

    }
