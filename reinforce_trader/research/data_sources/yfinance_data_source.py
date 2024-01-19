import os

import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup

from reinforce_trader.research.datalake_client import DatalakeClient


DATA_SOURCE = 'yfinance'


# Function to download historical data
def download_market_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
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


def update_data(dl_client, start_date, end_date):
    data_menu = dl_client.get_data_menu(DATA_SOURCE)
    for asset_type in data_menu:
        for asset in data_menu[asset_type]:
            if asset_type in ('stock', 'fx'):
                if asset_type == 'fx':
                    external_asset = f'{asset}=X'
                else:
                    external_asset = asset
                df = download_market_data(external_asset, start_date, end_date)

                columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
                df.columns =columns
                df.index.name = 'ts'  # the `Date` is set as index
                # Convert 'ts' column to datetime and set as index
                df.index = pd.to_datetime(df.index)
                # df.set_index('ts', inplace=True)

                dl_client.update_data(
                    DATA_SOURCE,
                    asset_type,
                    asset,
                    data=df,
                )
            else:
                raise ValueError(f'asset_type={asset_type} is not in the menu')


def add_data(dl_client: DatalakeClient, start_date: str, end_date: str):
    # prepare data menu
    sp500_list = download_sp500_list()
    sp500_stocks = [company['ticker'] for company in sp500_list]

    data_menu = {
        'stock': sp500_stocks,
        'fx': ['EURUSD', 'USDJPY', 'GBPUSD', 'AUDUSD', 'USDCHF', 'USDCAD', 'NZDUSD'],
    }

    # add_data in datalake
    dl_client.add_data_source(DATA_SOURCE, data_menu)

    for asset_type in data_menu:
        for asset in data_menu[asset_type]:
                
            if asset_type in ('fx', 'stock'):
                if asset_type == 'fx':
                    external_asset = f'{asset}=X'
                else:
                    external_asset = asset

                df = download_market_data(external_asset, start_date, end_date)
                columns = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
                df.columns =columns
                df.index.name = 'ts'  # the `Date` is set as index
                # Convert 'ts' column to datetime and set as index
                df.index = pd.to_datetime(df.index)
                # df.set_index('ts', inplace=True)

                dl_client.add_data(
                    DATA_SOURCE,
                    asset_type,
                    asset,
                    data=df,
                )

            else:
                raise ValueError(f'asset_type={asset_type} is not in the menu')


# def main():
#     action = 'add'
    
#     dl_client = DatalakeClient(os.path.abspath('./data'))

    

#     if action == 'add':
#         add_data(dl_client, start_date, end_date)
    
#     elif action == 'update':
#         update_data(dl_client, start_date, end_date)


# if __name__ == '__main__':
#     main()
