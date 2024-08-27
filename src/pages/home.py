"""
This is the home page of the app.
"""
import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Welcome to k8s-dash'),
])
