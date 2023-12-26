# deprecated: check features in research
import typing
import os

from tqdm import tqdm
import pandas as pd


def load_df(file_path) -> pd.DataFrame:
    df = pd.read_csv(file_path, header=0)
    return df


def build_labels(df: pd.DataFrame, r_stop: float, r_take: float, T: int, step_size: int=1) -> pd.DataFrame:
    """_summary_

    Args:
        df (pd.DataFrame): a pandas dataframe with columns `Date`, `Open`, `High`, `Low`, `Close`, `Adj Close`, `Volume`
        r_stop (float): the percentage loss for stop loss
        r_take (float): the percentage gain for take profit
        T (int): the horizon of trading
        step_size (int): the step size while moving the window

    Returns:
        pd.DataFrame: 1. the label (1 for take profit, -1 for stop loss, 0 for end of the horizon), 2. the actual return i.e exit_price - entry_price, 3. start date in yyyy-mm-dd, 4. end date in yyyy-mm-dd
    """
    labels = []
    for i in range(0, len(df) - T, step_size):
        entry_price = df['Close'].iloc[i]
        take_profit_price = entry_price * (1 + r_take)
        stop_loss_price = entry_price * (1 - r_stop)

        label = 0  # Default label (hold till end of horizon)
        final_price = df['Close'].iloc[i + T - 1]  # Default final price (price at the end of horizon)

        for j in range(i, i + T):
            day_high = df['High'].iloc[j]
            day_low = df['Low'].iloc[j]

            if day_high >= take_profit_price:
                label = 1  # Take profit
                final_price = take_profit_price
                break
            elif day_low <= stop_loss_price:
                label = -1  # Stop loss
                final_price = stop_loss_price
                break

        actual_return = final_price - entry_price
        start_date = df['Date'].iloc[i]
        end_date = df['Date'].iloc[j]  # The end date is now determined by when the condition was met

        labels.append((label, actual_return, start_date, end_date))

    df_labels = pd.DataFrame(labels, columns=['label', 'return', 'start_date', 'end_data'])
    return df_labels


def extract_pdt_from_file_name(file_name):
    return file_name.split('_')[0]


def main():
    # Define ranges for each parameter
    r_stop_values = [0.01, 0.02, 0.03]
    r_take_values = [0.02, 0.03, 0.04]
    T_values = [5, 7, 10]
    step_size_values = [1, 3, 7, 14, 28, 90, 180]

    raw_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/yfinance_fx_historical/raw_data'))
    label_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/yfinance_fx_historical/label_data'))

    if not os.path.exists(label_data_dir):
        os.mkdir(label_data_dir)

    for r_stop in r_stop_values:
        for r_take in r_take_values:
            for T in T_values:
                for step_size in step_size_values:
                    output_file_path = os.path.join(label_data_dir, f'labels-r_stop={r_stop}-r_take={r_take}-T={T}-step_size={step_size}.csv')
                    if not os.path.exists(output_file_path):
                        df_result = []
                        for file_name in tqdm(os.listdir(raw_data_dir)):
                            pdt = extract_pdt_from_file_name(file_name)
                            file_path = os.path.join(raw_data_dir, file_name)
                            df = load_df(file_path)

                            df_labels = build_labels(df, r_stop, r_take, T, step_size)
                            df_labels['pdt'] = pdt
                            df_result.append(pd.DataFrame(df_labels))

                        df_result = pd.concat(df_result)

                        df_result.to_csv(
                            output_file_path,
                            index=False
                        )


if __name__ == '__main__':
    main()


