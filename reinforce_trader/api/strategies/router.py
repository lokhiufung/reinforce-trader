from typing import Annotated
from bson import ObjectId

from fastapi import APIRouter, Depends, Request, Body
from pymongo import MongoClient

from reinforce_trader.api.strategies.models.strategy import Strategy
from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api.strategies import service as strategies_service
from reinforce_trader.api import config


# Create the APIRouter instance
strategies_router = APIRouter(
    prefix='/users/{user_id}/strategies',
    tags=['strategies'],
)


@strategies_router.post('/', status_code=201)
async def create_strategy(
    user_id,
    strategy: Strategy,
    db_client: MongoClient = Depends(get_db_client)
):  
    return strategies_service.create_strategy(user_id, strategy, db_client)


@strategies_router.get('/', status_code=200)
async def get_strategies(user_id, db_client: MongoClient = Depends(get_db_client)):
    return strategies_service.get_strategies(user_id, db_client)


@strategies_router.get("/{strategy_id}")
async def get_strategy(user_id: str, strategy_id: str, db_client: MongoClient = Depends(get_db_client)):
    return strategies_service.get_strategy(user_id, strategy_id, db_client)


@strategies_router.put('/{strategy_id}', status_code=200)
async def update_strategy(
        user_id: str,
        strategy_id: str, 
        name: Annotated[str, Body()],
        initial_cash: Annotated[float, Body()],
        db_client: MongoClient = Depends(get_db_client)
    ):
    return strategies_service.update_strategy(user_id, strategy_id, name, initial_cash, db_client)


@strategies_router.delete('/{strategy_id}', status_code=200)
async def delete_strategy(
        user_id: str,
        strategy_id: str,
        db_client: MongoClient = Depends(get_db_client)
    ):
    return strategies_service.delete_strategy(user_id, strategy_id, db_client)


# trade analytics
@strategies_router.get("/{strategy_id}/winrate")
async def get_winrate(request: Request, strategy_id: str, ticker: str=None, db_client: MongoClient = Depends(get_db_client)):
    return strategies_service.get_winrate(strategy_id, ticker, db_client)


@strategies_router.get("/{strategy_id}/profit_loss")
async def get_pnl(request: Request, strategy_id: str, ticker: str=None, db_client: MongoClient = Depends(get_db_client)):
    return strategies_service.get_pnl(strategy_id, ticker, db_client)