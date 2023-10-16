from fastapi import APIRouter, Request, Query

# from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api.historical_data import service as historical_data_service
from reinforce_trader.api.constants import * 


# Create the APIRouter instance
historical_data_router = APIRouter(
    prefix='/historical-data',
    tags=['historical-data'],
)

@historical_data_router.get('/')
def get_historical_data(request: Request, ticker: str = Query(..., alias='ticker'), start: str = None, end: str = None):
    return historical_data_service.get_historical_data(ticker, start, end)