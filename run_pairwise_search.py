from datetime import datetime, timedelta
from tqdm import tqdm
import pandas as pd
import concurrent.futures
import numpy as np

from reinforce_trader.research.metrics.codependency import get_mutual_information, get_variation_of_information
from reinforce_trader.research.datalake_client import DatalakeClient


# def get_metric(dl_client: DatalakeClient, asset_1, asset_2, data_source):
#     # directly load data in a seperate process
    
#     dfs = dl_client.get_tables(data_source, [asset_1, asset_2])
#     s_1, s_2 = dfs[asset_1]['close'].values, dfs[asset_1]['close'].values

#     vi = get_variation_of_information(s_1, s_2, bins=100, norm=True)
#     return vi


def get_metrics_batch(dl_client: DatalakeClient, asset_pairs, data_source, start_date, end_date):
    # Function to process a batch of asset pairs
    results = []
    for asset_1, asset_2 in asset_pairs:
        dfs = dl_client.get_tables(data_source, [asset_1, asset_2])
        # Convert 'ts' column to datetime and filter based on start_date and end_date
        df_1 = dfs[asset_1]
        df_1['ts'] = pd.to_datetime(df_1['ts'])
        df_1 = df_1[(df_1['ts'] >= pd.to_datetime(start_date)) & (df_1['ts'] <= pd.to_datetime(end_date))]

        df_2 = dfs[asset_2]
        df_2['ts'] = pd.to_datetime(df_2['ts'])
        df_2 = df_2[(df_2['ts'] >= pd.to_datetime(start_date)) & (df_2['ts'] <= pd.to_datetime(end_date))]

        # if the lengths are different, drop oldest rows from the larger df
        diff = len(df_1) - len(df_2)
        if diff > 0:
            # drop the first k rows from the df_1
            df_1 = df_1.iloc[diff:, :]
        elif diff < 0:
            df_2 = df_2.iloc[abs(diff):, :]
        s_1, s_2 = df_1['close'].values, df_2['close'].values
        try:
            vi = get_variation_of_information(s_1, s_2, bins=100, norm=True)
        except:
            vi = np.nan 
        results.append({'pair': f'{asset_1}_{asset_2}', 'metric': vi})
    return results


def main():
    data_source = 'yfinance'
    dl_client = DatalakeClient()
    data_menu = dl_client.get_data_menu(data_source)
    assets = data_menu['stock']
    end_date = datetime.today()
    # use trailling half year as the default start_date
    start_date = end_date - timedelta(days=30*3)

    batch_size = 20  # Set the batch size
    metrics = []

    # Generate all possible pairs
    all_pairs = [(assets[i], assets[j]) for i in range(len(assets)) for j in range(i + 1, len(assets))]

    # Process in batches using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(all_pairs), batch_size):
            batch = all_pairs[i:i + batch_size]
            futures.append(executor.submit(get_metrics_batch, dl_client, batch, data_source, start_date, end_date))

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            metrics.extend(future.result())

    df = pd.DataFrame(metrics)
    df.to_csv('./corr.csv', index=False, header=True)


if __name__ == '__main__':
    main()

