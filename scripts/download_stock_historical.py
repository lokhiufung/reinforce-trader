# deprecated: check datalake_client
import os
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

import yfinance as yf
from tqdm import tqdm
from reinforce_trader.logger import get_logger


logger = get_logger('download_sp500_historical.log', logger_lv='error')


# Function to download historical data
def download_stock_data(stock_symbol, start_date, end_date):
    data = yf.download(stock_symbol, start=start_date, end=end_date)
    return data


def download_sp500_list():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    companies = []

    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        ticker = cols[0].text.strip()
        company_name = cols[1].text.strip()
        cik = cols[6].text.strip()
        company = {
            'ticker': ticker,
            'company_name': company_name,
            'cik': cik
        }
        companies.append(company)

    return companies


def save_to_csv(data, filename):
    data.to_csv(filename, index=True)


def main():
    raw_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/yfinance_fx_historical/raw_data'))

    # List of S&P 500 stock symbols
    # Note: You will need to replace this with the actual list of S&P 500 stock symbols
    sp500_list = download_sp500_list()
    sp500_stocks = [company['ticker'] for company in sp500_list]

    # Setting the date range (10 years)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=10*365)

    # Downloading and saving data for each stock
    historical_data = {}
    for stock in tqdm(sp500_stocks):
        logger.info(f"Downloading data for {stock}")
        data = download_stock_data(stock, start_date, end_date)
        historical_data[stock] = data
        filename = f"{raw_data_dir}/{stock}_historical_data.csv"
        logger.info(f"Saving data to {filename}")
        save_to_csv(data, filename)


# Call the main function
if __name__ == "__main__":
    main()

