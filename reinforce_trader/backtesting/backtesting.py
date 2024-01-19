import numpy as np
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

from reinforce_trader.research.get_sequences import get_rolling_window_sequences


def plot_backtesting_results(df):
    fig = make_subplots(rows=5, cols=1, shared_xaxes=True, 
        subplot_titles=('Stock Price and Signals', 'Signal Over Time', 'Balance Over Time', 'Exposure Over Time'),
        vertical_spacing=0.1
    )
    # Create traces for Plotly: price, buy signals, sell signals, and balance
    price_trace = go.Scatter(x=df.index, y=df['close'], name='Stock Price', line=dict(color='blue', width=2))
    signals = go.Scatter(x=df.index, y=df['signal'], name='Signal', line=dict(color='blue', width=2))
    buy_signals = go.Scatter(x=df[df['action'] > 0].index,
                    y=df[df['action'] > 0]['close'],
                    mode='markers',
                    name='Buy Signals',
                    marker=dict(color='green', size=10, symbol='triangle-up')
                )
    sell_signals = go.Scatter(x=df[df['action'] < 0].index,
                        y=df[df['action'] < 0]['close'],
                        mode='markers',
                        name='Sell Signals',
                        marker=dict(color='red', size=10, symbol='triangle-down')
                    )
    balance_trace = go.Scatter(x=df.index, y=df['balance'], name='Balance', line=dict(color='purple', width=2, dash='dash'))
    exposure_trace = go.Scatter(x=df.index, y=df['exposure'], name='Exposure', line=dict(color='black', width=2, dash='dash'))
    portfolio_trace = go.Scatter(x=df.index, y=df['portfolio_value'], name='Portfolio', line=dict(color='black', width=2, dash='dash'))

    # Add traces to the figure
    fig.add_trace(price_trace, row=1, col=1)
    fig.add_trace(buy_signals, row=1, col=1)
    fig.add_trace(sell_signals, row=1, col=1)
    fig.add_trace(signals, row=2, col=1)
    fig.add_trace(balance_trace, row=3, col=1)
    fig.add_trace(exposure_trace, row=4, col=1)
    fig.add_trace(portfolio_trace, row=5, col=1)


    # Set up the layout for the figure
    fig.update_layout(
        title='Backtesting Results',
        xaxis_title='Date',
        xaxis2_title='Date',  # This is the shared x-axis for the balance subplot
        yaxis_title='Price (USD)',
        yaxis2_title='Balance (USD)',
        showlegend=False,  # Optional: hide the legend if it's not needed
        margin=dict(l=40, r=0, t=80, b=40)
    )

    # Update y-axis type for balance if needed (e.g., to 'log' type)
    fig.update_yaxes(title_text='Price (USD)', row=1, col=1)
    fig.update_yaxes(title_text='Signal', row=2, col=1)
    fig.update_yaxes(title_text='Balance (USD)', row=3, col=1)
    fig.update_yaxes(title_text='Exposure (USD)', row=4, col=1)
    fig.update_yaxes(title_text='Portfolio (USD)', row=5, col=1)


    # Update layout for shared x-axis (dates)
    # fig.update_xaxes(title_text='Date', row=1, col=1)
    # fig.update_xaxes(title_text='Date', row=2, col=1)
    fig.update_xaxes(title_text='Date', row=5, col=1)

    fig.show()



class Backtesting:
    def __init__(self):
        # consider only single asset now
        self.position = 0
        self.initial_balance = None
        self.balance = None
        self.avg_px = None
        self.df = None
    
    def update_avg_px(self, px, size):
        if self.avg_px is None:
            self.avg_px = px
        else:
            # only update when buying
            self.avg_px = (self.avg_px * self.position + px * size) / (self.position + size)
        return self.avg_px

    def add_data(self, df: pd.DataFrame):
        self.df = df

    def run(self, strategy, signaller, plot=True):

        # set balance from the strategy
        self.balance = strategy.get_balance()
        self.initial_balance = strategy.get_balance()

        window_size = signaller.window_size  # only the signaller knows the window_size
        sequences = get_rolling_window_sequences(self.df, window_size=window_size)

        signals = signaller.get_signals(sequences)
        df = self.df.iloc[window_size-1:, :]  # remove rows for preparation

        # actions = [strategy.on_signal(signal) for signal in signals]

        adjusted_actions = []
        # positions = []
        for signal, bar in zip(signals, df[['open', 'high', 'low', 'close', 'volume']].to_records()):
            action = strategy.on_bar(
                bar['open'],
                bar['high'],
                bar['low'],
                bar['close'],
                bar['volume'],
                signal=signal
            )  # REMINDER: bulk generating signals can be more efficient if using ML models
            if self.position + action < 0:
                # TODO: dont allow short selling
                action = 0
            ### refactor this part later
            if action > 0:
                self.update_avg_px(px=bar['close'], size=action)
                self.balance -= bar['close'] * action
            elif action < 0:
                # selling an asset doesnt affect the cost
                self.balance -= bar['close'] * action
            strategy.on_balance_update(balance=self.balance)
            self.position += action
            strategy.on_position_update(avg_px=self.avg_px, position=self.position)
            ###
            # positions.append(self.position)
            adjusted_actions.append(action)

        df['signal'] = signals
        df['action'] = adjusted_actions
        df['position'] = df['action'].cumsum()
        df['exposure'] = df['position'] * df['close']  # exposure in USD
        df['balance'] = self.initial_balance + (-1 * df['action'] * df['close']).cumsum()  # use the close price as entry price
        df['portfolio_value'] = df['exposure'] + df['balance']
        df = df.set_index('ts')
        if plot:
            plot_backtesting_results(df)

        return self.df
    

