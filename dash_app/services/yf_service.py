import yfinance as yf

    
def get_historical_data(ticker, start, end):
    return yf.download(ticker, start=start, end=end)
