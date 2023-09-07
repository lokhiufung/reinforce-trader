import os
import base64
from datetime import datetime
from bson import ObjectId
from bson.binary import Binary

from typing import List
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pymongo import MongoClient

from reinforce_trader.api.trades.models.trade import Trade
from reinforce_trader.api.constants import * 


DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print(DB_HOST)
print(DB_USERNAME)

# Connect to MongoDB
client = MongoClient(f"mongodb://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/")  # Update the connection string accordingly
db = client[DB_NAME]
trades_collection = db["trades"]

# Create the APIRouter instance
trades_router = APIRouter(
    prefix='/trades',
    tags=['trades'],
)


# create trade
@trades_router.post("/", response_model=None, status_code=201)
async def create_trade(
    strategy: str = Form(description="Name of the strategy"),
    ticker: str = Form(description="Name of the ticker (the standard ticker name)"),
    price: float = Form(description="the execution price of this trade"),
    tradeDate: str = Form(description="the execution date of this trade"),
    tradeSize: float = Form(description="the execution size of this trade"),
    tradeSide: int = Form(description="the direction of this trade (long / short)"),
    tradeNotes: str = Form(None, description="the notes for this trade (can be anything)"),
    image: UploadFile = File(None, description="the chart pattern indicating the snapshot / the reason of making this trade")
):
    trade_dict = Trade(
        strategy=strategy,
        ticker=ticker,
        price=price,
        tradeDate=tradeDate,
        tradeSize=tradeSize,
        tradeSide=tradeSide,
        tradeNotes=tradeNotes,
    ).dict(by_alias=True)
    # Parse the string into a datetime object
    trade_dict['tradeDate'] = datetime.strptime(trade_dict['tradeDate'], DATE_FORMAT)
    del trade_dict['_id']  # remove the None id field
    if image:
        # Read image into bytes
        image_bytes = image.file.read()
        # Store binary data in MongoDB document
        trade_dict['image'] = Binary(image_bytes)
    inserted_trade = trades_collection.insert_one(trade_dict)
    trade_dict['_id'] = str(inserted_trade.inserted_id)
    trade_dict['tradeDate'] = datetime.strftime(trade_dict['tradeDate'], DATE_FORMAT)
    return {
        "_id": trade_dict['_id'],
    }


@trades_router.get("/", response_model=List[Trade])
async def get_trades(request: Request, strategy: str = None, ticker: str = None):
    query = {}
    
    if strategy:
        query["strategy"] = strategy
    if ticker:
        query["ticker"] = ticker
    
    trades = list(trades_collection.find(query))
    for trade in trades:
        trade['_id'] = str(trade['_id'])
        trade['tradeDate'] = datetime.strftime(trade['tradeDate'], DATE_FORMAT)
        
        # Check if 'image' field exists and convert it to base64 string
        if 'image' in trade and trade['image'] is not None:
            trade['image'] = base64.b64encode(trade['image']).decode("utf-8")  # Convert binary data to base64 string
    
    return trades

@trades_router.get("/{trade_id}", response_model=Trade)
async def get_trade(trade_id: str):
    trade = trades_collection.find_one({"_id": ObjectId(trade_id)})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade['_id'] = str(trade['_id'])
    trade['tradeDate'] = datetime.strftime(trade['tradeDate'], DATE_FORMAT)
    # Check if 'image' field exists and convert it to base64 string
    if 'image' in trade and trade['image'] is not None:
        trade['image'] = base64.b64encode(trade['image']).decode("utf-8")  # Convert binary data to base64 string
    return trade


@trades_router.put("/{trade_id}", response_model=None)
async def update_trade(
    trade_id: str,
    strategy: str = Form(None, description="Name of the strategy"),
    ticker: str = Form(None, description="Name of the ticker (the standard ticker name)"),
    price: float = Form(None, description="the execution price of this trade"),
    tradeDate: str = Form(None, description="the execution date of this trade"),
    tradeSize: float = Form(None, description="the execution size of this trade"),
    tradeSide: int = Form(None, description="the direction of this trade (long / short)"),
    tradeNotes: str = Form(None, description="the notes for this trade (can be anything)"),
):
    existing_trade = trades_collection.find_one({"_id": ObjectId(trade_id)})
    if not existing_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    update_dict = {}
    if strategy is not None:
        update_dict["strategy"] = strategy
    if ticker is not None:
        update_dict["ticker"] = ticker
    if price is not None:
        update_dict["price"] = price
    if tradeDate is not None:
        update_dict["tradeDate"] = datetime.strptime(tradeDate, DATE_FORMAT)
    if tradeSize is not None:
        update_dict["tradeSize"] = tradeSize
    if tradeSide is not None:
        update_dict["tradeSide"] = tradeSide
    if tradeNotes is not None:
        update_dict["tradeNotes"] = tradeNotes

    trades_collection.update_one({"_id": ObjectId(trade_id)}, {'$set': update_dict})
    # trade['tradeDate'] = datetime.strftime(trade['tradeDate'], DATE_FORMAT)
    return {
        '_id': trade_id,
    }


@trades_router.delete("/{trade_id}", response_model=None, status_code=204)
async def delete_trade(trade_id: str):
    deleted_trade = trades_collection.find_one_and_delete({"_id": ObjectId(trade_id)})
    if not deleted_trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    deleted_trade["_id"] = str(deleted_trade["_id"])  # Convert ObjectId to str
    # deleted_trade['tradeDate'] = datetime.strftime(deleted_trade['tradeDate'], DATE_FORMAT)
    return {
        "_id": deleted_trade["_id"]
    }