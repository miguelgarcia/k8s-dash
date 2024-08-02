from dash import html

class NavBar(html.Nav):
    def __init__(self):
        super().__init__(
            className="navbar navbar-inverse navbar-fixed-top",
            children=[
                html.Div(
                    className="container-fluid",
                    children=[html.Div(
                        className="navbar-header",
                        children=[
                            html.A(className="navbar-brand", href="#", children="Kubedash")
                        ]
                    )]
                )
            ]
        )

class SideBar(html.Div):
    def __init__(self, pathname=""):
        super().__init__(
            className="col-sm-3 col-md-2 sidebar",
            children=[
                html.Ul(
                    className="nav nav-sidebar",
                    children=[
                        html.Li(
                            className="active" if "/" == pathname else "",
                            children=html.A("Overview", href="/")
                        ),
                        html.Li(
                            className="active" if "/deployments" in pathname else "",
                            children=html.A("Deployments", href="/deployments")
                        ),
                        html.Li(
                            className="active" if "/pods" in pathname else "",
                            children=html.A("Pods", href="/pods")
                        )
                    ]
                )
            ]
        )
