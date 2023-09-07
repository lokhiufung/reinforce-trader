from dash import html
import dash_bootstrap_components as dbc


# Define the navbar structure
def Navbar():
    layout = html.Div([
        dbc.NavbarSimple(
            children=[
                # dbc.NavItem(dbc.NavLink("Home", href="/")),
                dbc.NavItem(dbc.NavLink("Entry / Exit", href="/")),
                dbc.NavItem(dbc.NavLink("Trades", href="/trades")),
                dbc.NavItem(dbc.NavLink("New Trade", href="/add-trade")),
                # dbc.DropdownMenu(
                #     children=[
                #         dbc.DropdownMenuItem(strat, href=f"/strategies/{strat}") for strat in strats
                #     ],
                #     nav=True,
                #     in_navbar=True,
                #     label="Strategies"
                # ),
                # dbc.DropdownMenu(
                #     children=[
                #         dbc.DropdownMenuItem(ticker, href=f"/tickers/{ticker}") for ticker in tickers
                #     ],
                #     nav=True,
                #     in_navbar=True,
                #     label="Tickers"
                # ),
            ] ,
            brand="Trading Journal",
            brand_href="/",
            color="dark",
            dark=True,
        ), 
    ])

    return layout