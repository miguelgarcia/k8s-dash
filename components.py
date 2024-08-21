"""
This module contains the components that are used in the app.
"""
from dash import html
import dash_mantine_components as dmc


class NavBar(html.Div):
    def __init__(self):
        super().__init__([
                dmc.NavLink(label="Home", href="/"),
                dmc.NavLink(label="Deployments", href="/deployments"),
                dmc.NavLink(label="Pods", href="/pods"),
        ])
