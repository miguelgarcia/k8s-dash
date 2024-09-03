"""
This is the home page of the app.
"""
import dash
from dash import html
from dash_iconify import DashIconify

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Welcome to k8s-dash'),
    html.P('This is a simple dashboard to view and manage your Kubernetes cluster.'),
    html.A(href="https://github.com/miguelgarcia/k8s-dash", children=[
        "© 2024 Miguel Garcia",
        DashIconify(icon="bx:bxl-github", style={"margin-left": "0.5rem"})
    ])
])
