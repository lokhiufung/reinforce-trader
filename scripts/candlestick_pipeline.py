import os
import pandas as pd
import mplfinance as mpf
from tqdm import tqdm


def filter_by_year(df: pd.DataFrame, start_year: str, end_year: str) -> pd.DataFrame:
    """
    Filter the DataFrame to include data between the specified start and end years.

    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    start_year (str): The start year in 'YYYY' format.
    end_year (str): The end year in 'YYYY' format.

    Returns:
    pd.DataFrame: The filtered DataFrame.
    """
    # Ensure the 'Date' column is in datetime format
    # df['Date'] = pd.to_datetime(df['Date'])

    # Filter based on the year
    start_date = pd.to_datetime(f"{start_year}-01-01")
    end_date = pd.to_datetime(f"{end_year}-12-31")
    
    return df[(df.index >= start_date) & (df.index <= end_date)]


def calculate_label(window_data: pd.DataFrame, upper_barrier: float, lower_barrier: float):
    """
    Calculate the label using the Triple Barrier Method.

    Parameters:
    window_data (pd.DataFrame): The DataFrame containing the window of data.
    upper_barrier (float): The upper barrier as a percentage above the entry price.
    lower_barrier (float): The lower barrier as a percentage below the entry price.

    Returns:
    int: The label (1 for upper barrier hit, -1 for lower barrier hit, 0 for time barrier hit).
    """
    entry_price = window_data.iloc[0]['Close']
    upper_price = entry_price * (1 + upper_barrier)
    lower_price = entry_price * (1 - lower_barrier)

    for index, row in window_data.iterrows():
        if row['High'] >= upper_price:
            return 1  # Upper barrier hit
        if row['Low'] <= lower_price:
            return -1  # Lower barrier hit

    return 0  # Time barrier hit


def generate_candlestick_charts(df: pd.DataFrame, feature_window_size: int, label_window_size: int, save_path: str, step_size: int=1) -> None:
    """
    Generate candlestick charts and corresponding labels using the Triple Barrier Method.

    Parameters:
    csv_file_path (str): The file path of the CSV file.
    feature_window_size (int): The size of the window to create a chart for.
    label_window_size (int): The size of the window to calculate the label for.
    save_path (str): The path to save the chart images and labels.
    step_size (int): The number of steps to skip between each window.
    """
    # # Load data
    # df = pd.read_csv(csv_file_path)
    # df['Date'] = pd.to_datetime(df['Date'])
    # df.set_index('Date', inplace=True)

    # Define barriers
    upper_barrier = 0.01  # 1% above entry price
    lower_barrier = 0.01  # 1% below entry price

    if not os.path.exists(f'{save_path}/images'):
        os.mkdir(f'{save_path}/images')

    # Generate and save candlestick charts and labels
    for i in tqdm(range(0, len(df) - feature_window_size - label_window_size + 1, step_size)):
        feature_data = df.iloc[i:i + feature_window_size]
        label_data = df.iloc[i + feature_window_size:i + feature_window_size + label_window_size]

        # Calculate label
        label = calculate_label(label_data, upper_barrier, lower_barrier)

        # Save chart and label
        # Extract start and end dates from feature data
        start_date = feature_data.index[0].strftime('%Y-%m-%d')
        end_date = feature_data.index[-1].strftime('%Y-%m-%d')
        
        chart_path = f"{save_path}/images/chart_{start_date}_{end_date}.png"
        mpf.plot(feature_data, type='candle', savefig=chart_path)
        with open(f"{save_path}/labels.csv", 'a') as file:
            file.write(f"{start_date},{end_date},{chart_path},{label}\n")


def load_csv(file_path):
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    return df


def pipeline(file_path, output_path, start_year='2014', end_year='2016', feature_window_size=12*7, label_window_size=1*7, step_size=1):
    df = load_csv(file_path)
    # use 7, 14, 28 ... as weekly cycle
    # window_size should cover mulitple levels of trends
    # say the unit window_size = 7, then you should use k * 7 as the window size where k can be 2, 3, 4, ...
    df = filter_by_year(df, start_year, end_year)
    # Example usage
    generate_candlestick_charts(df, feature_window_size, label_window_size, output_path, step_size=step_size)


if __name__ == '__main__':
    file_path = './data/yfinance_fx_historical/raw_data/USDJPY_historical_data.csv'
    output_path = './data/yfinance_fx_historical/chart_data'

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    pipeline(
        file_path=file_path,
        output_path=output_path
    )