from fastapi import Depends
from reinforce_trader.api.trades.service import TradeService
from reinforce_trader.api.mongodb.dependencies import get_db_client


def get_trade_service(db_client: Depends[get_db_client]):
    return TradeService(
        db_client=db_client,
    )
