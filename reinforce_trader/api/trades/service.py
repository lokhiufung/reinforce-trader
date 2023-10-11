from datetime import datetime
from bson import ObjectId

import pymongo
from fastapi import HTTPException

from reinforce_trader.api import config
from reinforce_trader.api.mongodb import utils as mongodb_utils
from reinforce_trader.api.constants import * 


def create_trades(
    user_id,
    trade,
    db_client
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
    ## for strategy improvement
    # find all the related trades and determine if the trade is exit or entry
    trades = trades_collection.find({"uerId": user_id, "ticker": trade.ticker, "strategy": trade.strategy}).sort('date', pymongo.DESCENDING)
    trades = list(trades)
    position = mongodb_utils.get_current_position(trades_collection, user_id, trade.ticker, trade.strategy)
    if position * trade.side < 0:
        # if the current position is at the opposite side of side, exit
        trade_dict['action'] = -1  # -1 means exit
    else:
        trade_dict['action'] = 1  # 1 means entry

    # check if it is a winning / losing / even trade
    latest_trade = mongodb_utils.get_latest_trade(trades_collection, user_id, trade.ticker, trade.strategy)
    if trade.price - latest_trade['price'] > 0:
        trade_dict['label'] = 'win'
    elif trade.price - latest_trade['price'] < 0:
        trade_dict['label'] = 'loss'
    else:
        trade_dict['label'] = 'even'

    inserted_trade = trades_collection.insert_one(trade_dict)
    trade_dict['_id'] = str(inserted_trade.inserted_id)
    trade_dict['date'] = datetime.strftime(trade_dict['date'], DATE_FORMAT)
    return {
        "_id": trade_dict['_id'],
    }


def get_trades(user_id, strategy, ticker, db_client):
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
    return trades


def get_trade(user_id, trade_id, db_client):

    db = db_client[config.DB_NAME]
    trades_collection = db["trades"]

    trade = trades_collection.find_one({"_id": ObjectId(trade_id), "userId": user_id})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade['_id'] = str(trade['_id'])
    trade['date'] = datetime.strftime(trade['date'], DATE_FORMAT)
    return trade


def update_trade(user_id, trade_id, trade, db_client):
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


def delete_trade(user_id, trade_id, db_client):
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
