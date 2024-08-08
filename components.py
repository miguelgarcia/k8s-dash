import dash_bootstrap_components as dbc
from dash import html


class NavBar(html.Nav):
    def __init__(self):
        navbar = dbc.Navbar(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(dbc.NavbarBrand("Kubedash", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="#",
                    style={"textDecoration": "none"},
                ),
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink("Deployment", href="/deployments")),
                    dbc.NavItem(dbc.NavLink("Pods", href="/pods")),
                ])
            ],
            color="dark",
            dark=True,
        )
        super().__init__(navbar)
