import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash import Input, Output
from datetime import date

from dash_app.services.api_server_service import create_trade


dash.register_page(__name__, path="/add-trade")


def TradeFormRow(label, input_component):
    return dbc.Row(
        [
            dbc.Label(label, width=2),
            dbc.Col(
                input_component,
                width=10,
            )
        ],
        className='mb-3'
    )

def layout():
    strategy_input = TradeFormRow(
        'Strategy',
        input_component=dbc.Input(id='strategy-input', placeholder='Enter strategy', type='text')
    )
    ticker_input = TradeFormRow(
        'Ticker',
        input_component=dbc.Input(id='ticker-input', placeholder='Enter ticker', type='text')
    )
    price_input = TradeFormRow(
        'Price',
        input_component=dbc.Input(id='price-input', placeholder='Enter price', type='text')
    )
    trade_date_input = TradeFormRow(
        'Trade Date',
        input_component=dcc.DatePickerSingle(id='trade-date-picker', date=date.today())
    )
    trade_size_input = TradeFormRow(
        'Trade Size',
        input_component=dbc.Input(id='trade-size-input', placeholder='Enter trade size, e.g 100', type='text')
    )
    trade_side_input = TradeFormRow(
        'Trade Side',
        input_component=dbc.Input(id='trade-side-input', placeholder='Enter trade side, e.g 1', type='text')
    )
    trade_notes_input = TradeFormRow(
        'Trade Notes',
        input_component=dbc.Textarea(id='trade-notes-input', placeholder='Enter trade notes')
    )

    # Using Dash's dcc.Upload for image upload
    image_input = TradeFormRow(
        'Image',
        input_component=dcc.Upload(
            id='upload-image',
            children=html.Button('Upload Image'),
            multiple=False  # Allow single file
        )
    )
    submit_button = html.Button('Submit', id='submit-button')

    layout = html.Div([
        html.H1('Add a New Trade'),
        dbc.Form([
            strategy_input,
            ticker_input,
            price_input,
            trade_date_input,
            trade_side_input,
            trade_size_input,
            trade_notes_input,
            image_input,
            submit_button,
        ]),
        html.Div(id='form-output')

    ])
    return layout


@dash.callback(
    Output('form-output', 'children'),  # This is a placeholder; you'll need to add a location in your layout for form outputs or errors.
    [
        Input('submit-button', 'n_clicks'),
        Input('strategy-input', 'value'),
        Input('ticker-input', 'value'),
        Input('price-input', 'value'),
        Input('trade-date-picker', 'date'),
        Input('trade-size-input', 'value'),
        Input('trade-side-input', 'value'),
        Input('trade-notes-input', 'value'),
        Input('upload-image', 'contents'),
    ]
)
def submit_form(n_clicks, strategy, ticker, price, trade_date, trade_side, trade_size, trade_notes, uploaded_image):
    if n_clicks is None:
        return None  # Button has not been clicked
    
    # Validate form data
    if not all([strategy, ticker, price, trade_date, trade_side, trade_size, trade_notes]):
        return dbc.Alert("All fields must be filled out before submitting.", color="danger")

    # Prepare your form data
    form_data = {
        'strategy': str(strategy),
        'ticker': str(ticker),
        'price': float(price),
        'trade_date': trade_date,
        'trade_side': int(trade_side),
        'trade_size': float(trade_size),
        'trade_notes': str(trade_notes),
        'image': uploaded_image.split(',')[1] if uploaded_image else None  # Assuming the image is base64 encoded and prepended with MIME type
    }

    # Post the form data to the API
    msg = create_trade(**form_data)

    return dbc.Alert(msg, color="success" if 'Error' not in msg else "danger")


