import requests
from bs4 import BeautifulSoup
import yaml


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


def main():
    template = {}
    template['data_sources'] = {}
    template['data_sources']['yfinance'] = {}

    tickers = []
    # stock
    # List of S&P 500 stock symbols
    # Note: You will need to replace this with the actual list of S&P 500 stock symbols
    sp500_list = download_sp500_list()
    sp500_stocks = [company['ticker'] for company in sp500_list]
    tickers += sp500_stocks
    # fx
    fx_pairs = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCHF=X', 'USDCAD=X', 'NZDUSD=X']
    tickers += fx_pairs

    template['data_sources']['yfinance']['tickers'] = tickers
    
    with open('datalake_template.yaml', 'w') as f:
        # The default_flow_style=False argument makes the output more human-readable by using block style (every item in a new line) instead of flow style (inline).
        yaml.dump(template, f, default_flow_style=False)


if __name__ == '__main__':
    main()
    