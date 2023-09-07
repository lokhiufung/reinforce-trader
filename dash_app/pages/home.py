from datetime import datetime, timedelta

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import Input, Output
import plotly.graph_objects as go

from dash_app.services.api_server_service import get_trades
from dash_app.services.yf_service import get_historical_data


dash.register_page(__name__, path="/")


def layout():
    layout = html.Div([
        html.H1("Entry and Exit"),
        dcc.Dropdown(
            id='strategy-dropdown',
            options=[
                {'label': 'Strategy A', 'value': 'A'},
                {'label': 'Strategy B', 'value': 'B'},
                # Add more strategies here
            ],
            value='A',  # Default value
            multi=False
        ),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[
                {'label': 'TSLA', 'value': 'TSLA'},
                {'label': 'GOOGL', 'value': 'GOOGL'},
                # Add more strategies here
            ],
            value='GOOGL',  # Default value
            multi=False
        ),
        dcc.Graph(id='trade-journal-graph'),
    ])
    return layout


# Callback to update trade journal graph based on strategy selection
@dash.callback(
    Output('trade-journal-graph', 'figure'),
    [Input('strategy-dropdown', 'value'), Input('ticker-dropdown', 'value')]
)
def update_graph(selected_strategy, selected_ticker):
    trades_df = get_trades(selected_strategy, selected_ticker)
    
    if trades_df.empty:
        return go.Figure()
    
    # Fetch stock data using yfinance within the range of trades
    min_date = trades_df['tradeDate'].min()
    max_date = trades_df['tradeDate'].max()

    # Convert to datetime and expand the date range by about a month (30 days)
    min_date_dt = datetime.strptime(min_date, '%Y-%m-%d') - timedelta(days=1*30)
    max_date_dt = datetime.strptime(max_date, '%Y-%m-%d') + timedelta(days=1*30)

    # Convert back to string format
    min_date = min_date_dt.strftime('%Y-%m-%d')
    max_date = max_date_dt.strftime('%Y-%m-%d')

    # Fetch stock data using yfinance
    ticker = trades_df['ticker'].iloc[0]
    
    stock_data = get_historical_data(ticker, start=min_date, end=max_date)

    # Create a candlestick chart
    fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                        open=stock_data['Open'],
                                        high=stock_data['High'],
                                        low=stock_data['Low'],
                                        close=stock_data['Close'])])

    # Add entry and exit points from the trade journal
    entry_points = trades_df[trades_df['tradeSide'] == 1]
    exit_points = trades_df[trades_df['tradeSide'] == -1]
    
    fig.add_trace(go.Scatter(x=entry_points['tradeDate'], y=entry_points['price'], mode='markers', name='Entry', marker=dict(color='green')))
    fig.add_trace(go.Scatter(x=exit_points['tradeDate'], y=exit_points['price'], mode='markers', name='Exit', marker=dict(color='red')))

    return fig

