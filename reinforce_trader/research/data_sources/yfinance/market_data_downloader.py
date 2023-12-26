
import yfinance as yf


# Function to download historical data
def download_fx_data(fx_pair, start_date, end_date):
    data = yf.download(fx_pair, start=start_date, end=end_date)
    return data


def save_to_csv(data, filename):
    data.to_csv(filename, index=True)


def market_data_downloader(ticker, start_date, end_date):
    
    # Downloading and saving data for each FX pair
    historical_data = {}
    data = download_fx_data(ticker, start_date, end_date)
    historical_data[ticker] = data
    if '=' in ticker:
        ticker = ticker.split('=')[0]
    filename = f"./data/raw_data/{ticker}_historical_data.csv"
    
    save_to_csv(data, filename)
