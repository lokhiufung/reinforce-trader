import typing
import os
from datetime import datetime, timedelta
from importlib import import_module

import yaml
import pandas as pd


# data lake client object: for data selection, loading and transformation
class DatalakeClient:
    def __init__(self, datalake_dir, template_file_path):
        self.datalake_dir = datalake_dir
        self.template_file_path = template_file_path

        with open(self.template_file_path, 'r') as f:
            self.template = yaml.safe_load(f)

    def download_all(self):
        # Setting the date range (10 years)
        end_date = datetime.today()
        start_date = end_date - timedelta(days=10*365)

        for data_src in self.template['data_sources']:
            for ticker in self.template['data_sources']['yfinance']['tickers']:
                self.download(
                    data_src,
                    data_type='market_data',
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                )

    def download(self, data_src, data_type, ticker, start_date, end_date):
        downloader = import_module(f'reinfoce_trader.research.data_souces.{data_src}.{data_type}_downloader')
        downloader.market_data_downloader(ticker, start_date, end_date)
    
    def get_file_path(self, data_src, ticker, ver='raw_data'):
        return os.path.join(self.datalake_dir, f'{data_src}/{ver}/{ticker}_historical_data.csv')
    
    def get_table(self, data_src, ticker: str) -> pd.DataFrame:
        file_path = self.get_file_path(data_src, ticker, ver='raw_data')
        df = pd.read_csv(file_path, header=0)
        return df

    def get_tables(self, tickers: typing.List[str]) -> typing.Dict[str, pd.DataFrame]:
        tables = {}
        for ticker in tickers:
            df = self.get_table(ticker)
            tables[ticker] = df
        return tables
    
