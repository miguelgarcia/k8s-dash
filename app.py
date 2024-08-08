import logging
import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from components import NavBar
from kubernetes import config

config.load_kube_config()

app = Dash(__name__, title="kubedash", use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container([
    NavBar(),
    dbc.Container(dash.page_container, fluid=True)
], fluid=True, style={"margin": "0", "padding": 0})

if __name__ == '__main__':
    app.run_server(debug=True)
