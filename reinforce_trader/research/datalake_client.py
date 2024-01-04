import typing
import os
from datetime import datetime, timedelta
from importlib import import_module

import yaml
import pandas as pd


# data lake client object: for data selection, loading and transformation
class DatalakeClient:
    DEFAULT_DATALAKE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
    def __init__(self, datalake_dir=None):
        self.datalake_dir = datalake_dir
        if not self.datalake_dir:
            self.datalake_dir = self.DEFAULT_DATALAKE_DIR

        # self.template_file_path = template_file_path

        # with open(self.template_file_path, 'r') as f:
        #     self.template = yaml.safe_load(f)

    def get_data_sources(self):
        return os.listdir(self.datalake_dir)
    
    def get_data_menu(self, data_source):
        # load the data_menu first
        with open(os.path.join(self.datalake_dir, f'{data_source}_data_menu.yaml'), 'r') as f:
            data_menu = yaml.safe_load(f)
        return data_menu
    
    def add_data_source(self, data_source, data_menu):
        assert not data_source in self.get_data_sources()

        # register a new datalake for a new data_source and register a data_menu for it
        if data_source not in self.get_data_sources():
            os.mkdir(os.path.join(self.datalake_dir, data_source))

        # write the data_menu into the datalake_dir
        with open(os.path.join(self.datalake_dir, f'{data_source}_data_menu.yaml'), 'w') as f:
            yaml.safe_dump(data_menu, f)

        os.mkdir(os.path.join(self.datalake_dir, data_source, 'raw_data'))

    def add_data(self, data_source: str, asset_type: str, asset: str, data: pd.DataFrame):
        assert data_source in self.get_data_sources()
        
        file_path = self.get_file_path(data_source, asset, 'raw_data')

        assert not os.path.exists(file_path)  # ensure the adding data only at initialization, use update data later on

        # load the data_menu first
        with open(os.path.join(self.datalake_dir, f'{data_source}_data_menu.yaml'), 'r') as f:
            data_menu = yaml.safe_load(f)

        assert asset_type in data_menu
        assert asset in data_menu[asset_type]
        
        data.to_csv(
            file_path,
            index=True,
            header=True,
        )

    def update_data(self, data_source: str, asset_type: str, asset: str, data: pd.DataFrame):
        assert data_source in self.get_data_sources()

        # load the data_menu first
        with open(os.path.join(self.datalake_dir, f'{data_source}_data_menu.yaml'), 'r') as f:
            data_menu = yaml.safe_load(f)

        assert asset_type in data_menu
        assert asset in data_menu[asset_type]
        
        # old_data = pd.read_csv(
        #     os.path.join(self.datalake_dir, data_source, 'raw_data', f'{asset}_historical_data.csv'),
        #     header=0,
        #     # TODO: load schema from the template
        # )
        file_path = self.get_file_path(data_source, asset, 'raw_data')

        old_data = self.get_table(data_source, asset, set_index=True)
        self._merge_and_write_data(file_path, old_data, new_data=data)

    @staticmethod
    def _merge_and_write_data(file_path:str, old_data: pd.DataFrame, new_data: pd.DataFrame) -> pd.DataFrame:
        """
        Merges old_data and new_data DataFrames on the time dimension.
        In case of overlap, the rows from new_data are used.

        Parameters:
        old_data (pd.DataFrame): The old DataFrame.
        new_data (pd.DataFrame): The new DataFrame to merge.
        time_column (str): The name of the column representing time.

        Returns:
        pd.DataFrame: The merged DataFrame.
        """
        # Concatenate and sort by time
        merged_data = pd.concat([old_data, new_data]).sort_index()

        # Remove duplicate times, keeping the last (which comes from new_data)
        merged_data = merged_data[~merged_data.index.duplicated(keep='last')]

        # merged_data = merged_data.reset_index(drop=True)
        merged_data.to_csv(
            file_path,
            index=True,
            header=True,
        )

    # def download_all(self):
    #     # Setting the date range (10 years)
    #     end_date = datetime.today()
    #     start_date = end_date - timedelta(days=10*365)

    #     for data_src in self.template['data_sources']:
    #         for ticker in self.template['data_sources']['yfinance']['tickers']:
    #             self.download(
    #                 data_src,
    #                 data_type='market_data',
    #                 ticker=ticker,
    #                 start_date=start_date,
    #                 end_date=end_date,
    #             )

    # def download(self, data_src, data_type, ticker, start_date, end_date):
    #     downloader = import_module(f'reinfoce_trader.research.data_souces.{data_src}.{data_type}_downloader')
    #     downloader.market_data_downloader(ticker, start_date, end_date)
    
    def get_file_path(self, data_source, ticker, ver='raw_data'):
        return os.path.join(self.datalake_dir, f'{data_source}/{ver}/{ticker}_historical_data.csv')
    
    def get_table(self, data_source, ticker: str, set_index=False) -> pd.DataFrame:
        file_path = self.get_file_path(data_source, ticker, ver='raw_data')
        df = pd.read_csv(file_path, header=0)
        if set_index:
            df['ts'] = pd.to_datetime(df['ts'])
            df.set_index('ts', inplace=True)
        return df

    def get_tables(self, data_source, tickers: typing.List[str]) -> typing.Dict[str, pd.DataFrame]:
        tables = {}
        for ticker in tickers:
            df = self.get_table(data_source, ticker)
            tables[ticker] = df
        return tables
    
