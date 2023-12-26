import os

from tqdm import tqdm
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup


RAW_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/yfinance_fx_historical/raw_data'))
CORR_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/yfinance_fx_historical/corr_data'))


def load_df(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=0)
    return df


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


def get_return_correlation(ticker_1, ticker_2):
    df_1 = load_df(
        file_path=os.path.join(RAW_DATA_DIR, f'{ticker_1}_historical_data.csv')
    )
    df_2 = load_df(
        file_path=os.path.join(RAW_DATA_DIR, f'{ticker_2}_historical_data.csv')
    )
    
    # Set the `Date` column as index
    df_1.set_index('Date', inplace=True)
    df_2.set_index('Date', inplace=True)

    if df_1.empty or df_2.empty:
        return None    

    # Calculate returns
    df_1['return'] = df_1['Close'].pct_change()
    df_2['return'] = df_2['Close'].pct_change()
    
    # Join 2 dataframes on Date index
    joined_df = df_1[['return']].join(df_2[['return']], lsuffix='_1', rsuffix='_2', how='inner')
    
    # Drop the NaN rows that result from shifting
    joined_df.dropna(inplace=True)
    
    # Calculate and return the correlation of returns
    return joined_df['return_1'].corr(joined_df['return_2'])


if __name__ == '__main__':
    companies = download_sp500_list()
    tickers = [company['ticker'] for company in companies]
    n = len(tickers)

    corr_mat = np.zeros((n, n))
    
    for i in tqdm(range(n)):
        for j in range(n):
            if i <= j:
                corr = get_return_correlation(tickers[i], tickers[j])
                corr_mat[i, j] = corr
                corr_mat[j, i] = corr  # Fill in the symmetric value
    
    df_corr = pd.DataFrame(corr_mat, columns=tickers, index=tickers)
    df_corr.to_csv(
        os.path.join(CORR_DATA_DIR, 'corr_sp500_all.csv'),
    )
