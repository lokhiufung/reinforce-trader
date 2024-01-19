# deprecated: check datalake_client
from datetime import datetime, timedelta

import yfinance as yf

from reinforce_trader.logger import get_logger


logger = get_logger('download_fx_historical.log', logger_lv='debug')


# Function to download historical data
def download_fx_data(fx_pair, start_date, end_date):
    data = yf.download(fx_pair, start=start_date, end=end_date)
    return data


def save_to_csv(data, filename):
    data.to_csv(filename, index=True)


def main():
    # List of popular FX trading pairs
    fx_pairs = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCHF=X', 'USDCAD=X', 'NZDUSD=X']

    # Setting the date range (10 years)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=10*365)

    # Downloading and saving data for each FX pair
    historical_data = {}
    for pair in fx_pairs:
        logger.info(f"Downloading data for {pair}")
        data = download_fx_data(pair, start_date, end_date)
        historical_data[pair] = data
        filename = f"./data/raw_data/{pair.replace('=X', '')}_historical_data.csv"
        logger.info(f"Saving data to {filename}")
        save_to_csv(data, filename)
