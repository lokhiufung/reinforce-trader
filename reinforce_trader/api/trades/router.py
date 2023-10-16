from fastapi import APIRouter, Request, Depends
from pymongo import MongoClient

from reinforce_trader.api.trades.models.trade import Trade
from reinforce_trader.api.trades import service as trades_service
from reinforce_trader.api.mongodb.dependencies import get_db_client
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
    return trades_service.create_trades(user_id, trade, db_client)


@trades_router.get("/")
async def get_trades(request: Request, user_id: str, strategy: str = None, ticker: str = None, db_client: MongoClient = Depends(get_db_client)):
    return trades_service.get_trades(request, user_id, strategy, ticker, db_client)


@trades_router.get("/{trade_id}", response_model=Trade)
async def get_trade(user_id: str, trade_id: str, db_client: MongoClient = Depends(get_db_client)):
    return trades_service.get_trade(user_id, trade_id, db_client)


@trades_router.put("/{trade_id}", response_model=None)
async def update_trade(
    user_id: str,
    trade_id: str,
    trade: Trade,
    db_client: MongoClient = Depends(get_db_client)
):
    return trades_service.update_trade(user_id, trade_id, trade, db_client)


@trades_router.delete("/{trade_id}", response_model=None, status_code=204)
async def delete_trade(user_id: str, trade_id: str, db_client: MongoClient = Depends(get_db_client)):
    return trades_service.delete_trade(user_id, trade_id, db_client)
