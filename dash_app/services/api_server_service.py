import os
import base64
import io

import requests
import pandas as pd


API_SERVER_HOST = os.getenv('API_SERVER_HOST', 'localhost')
API_SERVER_PORT = os.getenv('API_SERVER_PORT', '8000')
API_SERVER_URL = f'http://{API_SERVER_HOST}:{API_SERVER_PORT}'


def get_tickers():
    response = requests.get(f'{API_SERVER_URL}/tickers')
    tickers = response.json()
    return tickers


def get_strategies():
    response = requests.get(f'{API_SERVER_URL}/strategies')
    strategies = response.json()
    return strategies


# Fetch trade data from FastAPI backend based on selected strategy
def get_trades(strat, ticker):
    response = requests.get(f'{API_SERVER_URL}/trades?strategy={strat}&ticker={ticker}')
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()


def create_trade(strategy, ticker, price, trade_date, trade_side, trade_size, trade_notes, image):
    data = {
        'strategy': strategy,
        'ticker': ticker,
        'price': price,
        'tradeDate': trade_date,
        'tradeSide': trade_side,
        'tradeSize': trade_size,
        'tradeNotes': trade_notes,
    }

    image_data = None
    if image:
        image_data = base64.b64decode(image)
        image_file = io.BytesIO(image_data)
        image_file.name = 'your_image_name_here.png'  # give it a name, could be dynamic
        image_file.seek(0)

    files = {'image': image_file} if image_file else None

    response = requests.post(f'{API_SERVER_URL}/trades', data=data, files=files)
    # Do something with the response
    if response.status_code == 201:
        return 'Trade successfully created!'
    else:
        return f'Failed to create trade. Error: {response.content}'


def update_trade(strategy, ticker, price, trade_date, trade_side, trade_size, trade_notes):
    data = {
        'strategy': strategy,
        'ticker': ticker,
        'price': price,
        'tradeDate': trade_date,
        'tradeSide': trade_side,
        'tradeSize': trade_size,
        'tradeNotes': trade_notes,
    }

    response = requests.post(f'{API_SERVER_URL}/trades', data=data)
    # Do something with the response
    if response.status_code == 201:
        return 'Trade successfully updated!'
    else:
        return f'Failed to update trade. Error: {response.content}'
    

def get_historical_data(ticker, start, end):
    response = requests.get(f'{API_SERVER_URL}/historical-data', params={'ticker': ticker, 'start': start, 'end': end})
    df = pd.DataFrame(response.json())
    return df