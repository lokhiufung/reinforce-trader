from dash import html
import dash
import dash_bootstrap_components as dbc

from dash_app.components.navbar import Navbar


def create_dash_app():

    # TICKERS = []
    # STRATS = []

    app = dash.Dash(__name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP], 
        meta_tags=[{"name": "viewport", "content": "width=device-width"}],
        # suppress_callback_exceptions=True,
        use_pages=True,
    )
    # Define the index page layout
    app.layout = html.Div([
        Navbar(),
        dash.page_container
    ])

    return app


if __name__ == '__main__':
    app = create_dash_app()
    app.run(host='0.0.0.0', port=8050)