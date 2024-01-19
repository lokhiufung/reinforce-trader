from reinforce_trader.backtesting.backtesting import Backtesting
from reinforce_trader.backtesting.strategies.buy_and_hold_strategy import BuyAndHoldStrategy
from reinforce_trader.backtesting.signallers.buy_and_hold_signaller import BuyAndHoldSignaller
from reinforce_trader.research.datalake_client import DatalakeClient


def main():
    start_date = '2021-01-01'
    end_date = '2023-12-31'
    window_size = 28

    dl_client = DatalakeClient()
    df = dl_client.get_table('yfinance', 'GOOGL', start_date=start_date, end_date=end_date)

    bt = Backtesting()
    bt.add_data(df)

    strategy = BuyAndHoldStrategy(
        initial_balance=100*1000,
        bet_size=1.0
    )
    signaller = BuyAndHoldSignaller(window_size=window_size)

    bt.run(strategy, signaller, plot=True)


if __name__ == '__main__':
    main()

