import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, dash_table
from dash import Input, Output

from dash_app.services.api_server_service import get_trades


dash.register_page(__name__, path="/trades")


def layout():
    layout = html.Div([
        html.H1("Chart Patterns"),
        dcc.Dropdown(
            id='strategy-dropdown-pattern',
            options=[
                {'label': 'Strategy A', 'value': 'A'},
                {'label': 'Strategy B', 'value': 'B'},
                # Add more strategies here
            ],
            value='A',  # Default value
            multi=False
        ),
        dcc.Dropdown(
            id='ticker-dropdown-pattern',
            options=[
                {'label': 'TSLA', 'value': 'TSLA'},
                {'label': 'GOOGL', 'value': 'GOOGL'},
                # Add more strategies here
            ],
            value='GOOGL',  # Default value
            multi=False
        ),
        html.Div(id='image-section'),
        dash_table.DataTable(id='trade-table', row_selectable='single', selected_rows=[0]),
        html.Div(id='trade-data-store', style={'display': 'none'}),  # hidden div to store df
    ])
    return layout


@dash.callback(
    [Output('image-section', 'children'), Output('trade-table', 'data'), Output('trade-table', 'selected_rows'), Output('trade-data-store', 'children')],
    [Input('strategy-dropdown-pattern', 'value'), Input('ticker-dropdown-pattern', 'value'), Input('trade-table', 'selected_rows')]
)
def update_trade_table(selected_strategy, selected_ticker, selected_rows):
    selected_row = selected_rows[0]
    trades_df = get_trades(selected_strategy, selected_ticker)
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