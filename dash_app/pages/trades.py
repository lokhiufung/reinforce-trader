import base64

import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from dash import Input, Output, State

from dash_app.services import api_server_service


dash.register_page(__name__, path="/trades")


def layout():
    tickers = api_server_service.get_tickers()
    strategies = api_server_service.get_strategies()

    layout = html.Div([
        html.H1("Chart Patterns"),
        dcc.Dropdown(
            id='strategy-dropdown-pattern-1',
            options=[{'label': strategy, 'value': strategy} for strategy in strategies],
            value=strategies[0],  # Default value
            multi=False
        ),
        dcc.Dropdown(
            id='ticker-dropdown-pattern-1',
            options=[{'label': ticker, 'value': ticker} for ticker in tickers],
            value=tickers[0],  # Default value
            multi=False
        ),
        html.A(
            'Download Data as CSV',
            id='download-link',
            download='trade_data.csv',
            href="",
            target="_blank",
        ),
        html.Div(id='image-section'),
        dash_table.DataTable(id='trade-table', row_selectable='single', selected_rows=[0], editable=True),
        html.Div(id='trade-data-store', style={'display': 'none'}),  # hidden div to store df
        dcc.Interval(
            id='interval-component',
            interval=30*1000, # in miliseconds,
            n_intervals=0
        )
    ])
    return layout


@dash.callback(
    [Output('image-section', 'children'), Output('trade-table', 'data'), Output('trade-table', 'selected_rows'), Output('trade-data-store', 'children')],
    [Input('strategy-dropdown-pattern-1', 'value'), Input('ticker-dropdown-pattern-1', 'value'), Input('trade-table', 'selected_rows')]
)
def update_trade_table(selected_strategy, selected_ticker, selected_rows):
    selected_row = selected_rows[0] if selected_rows else 0
    trades_df = api_server_service.get_trades(selected_strategy, selected_ticker)
    if trades_df.empty:
        return None, [], [], None
    
    # Serialize DataFrame to JSON and store in hidden Div
    trades_df_json = trades_df.to_json(date_format='iso', orient='split')

    # Assume image is in 'image' column and encoded in base64
    encoded_image = trades_df.iloc[selected_row]['image']
    image_element = html.Div([
        html.Img(src=f'data:image/png;base64,{encoded_image}')
    ], style={'textAlign': 'center'})
    
    # Exclude the 'image' column from the table
    table_data = trades_df.drop(columns=['image']).to_dict('records')

    return image_element, table_data, [selected_row], trades_df_json


@dash.callback(
    [Output('strategy-dropdown-pattern-1', 'options'), Output('ticker-dropdown-pattern-1', 'options')],
    [Input('interval-component', 'n_intervals')]
)
def update_options(n):
    tickers = api_server_service.get_tickers()
    strategies = api_server_service.get_strategies()
    
    ticker_options = [{'label': ticker, 'value': ticker} for ticker in tickers]
    strategy_options = [{'label': strategy, 'value': strategy} for strategy in strategies]
    
    return strategy_options, ticker_options


@dash.callback(
    Output('download-link', 'href'),
    [Input('trade-data-store', 'children')]
)
def generate_download_link(trades_df_json):
    if trades_df_json is None:
        return ''
    
    trades_df = pd.read_json(trades_df_json, orient='split')
    csv_string = trades_df.to_csv(index=False)
    csv_string_base64 = base64.b64encode(csv_string.encode()).decode()
    
    return f'data:text/csv;base64,{csv_string_base64}'


