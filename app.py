import logging
import dash
from dash import callback, html, Dash, dcc, callback, Input, Output
from components import NavBar, SideBar
from kubernetes import config

config.load_kube_config()

app = Dash(__name__, title="kubedash", use_pages=True)

app.layout = html.Div([
    dcc.Location(id="url"),
    NavBar(),
    html.Div(
        className="container-fluid",
        children=html.Div(
            className="row",
            children=[
                html.Div(SideBar(), id="sidebar-container"),
                html.Div(dash.page_container, className="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main")
            ]
        )
    )
])

@callback(Output("sidebar-container", "children"), Input("url", "pathname"))
def update_sidebar(pathname):
    return SideBar(pathname)

if __name__ == '__main__':
    app.run_server(debug=False)
