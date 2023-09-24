    
from datetime import datetime, timedelta
import yfinance as yf

from fastapi import APIRouter, HTTPException, Request, Query

# from reinforce_trader.api.mongodb.dependencies import get_db_client
from reinforce_trader.api.constants import * 


# Create the APIRouter instance
historical_data_router = APIRouter(
    prefix='/historical-data',
    tags=['historical-data'],
)

@historical_data_router.get('/')
def get_ohlcv(request: Request, ticker: str = Query(..., alias='ticker'), start: str = None, end: str = None):
    
    if ticker is None:
        raise HTTPException(status_code=400, detail="Ticker is required.")

    # Set the end date to today if not provided
    if end is None:
        end = datetime.today().strftime('%Y-%m-%d')
    
    # Set the start date to 3 months before the end date if not provided
    if start is None:
        end_date_obj = datetime.strptime(end, '%Y-%m-%d')
        start_date_obj = end_date_obj - timedelta(days=90)  # 3 months assumed to be 90 days
        start = start_date_obj.strftime('%Y-%m-%d')

    df = yf.download(ticker, start=start, end=end)
    return df.to_dict('records')  # Converting DataFrame to dictionary for JSON serialization
