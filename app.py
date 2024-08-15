import logging
import dash
import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, html
from kubernetes import config
from components import NavBar
_dash_renderer._set_react_version("18.2.0")

config.load_kube_config()

app = Dash(external_stylesheets=dmc.styles.ALL, use_pages=True, title="kubedash")

config.load_kube_config()

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={
        "primaryColor": "indigo",
        "fontFamily": "'Inter', sans-serif",
        "components": {
            "Button": {"defaultProps": {"fw": 400}},
            "Alert": {"styles": {"title": {"fontWeight": 500}}},
            "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
            "Badge": {"styles": {"root": {"fontWeight": 500}}},
            "Progress": {"styles": {"label": {"fontWeight": 500}}},
            "RingProgress": {"styles": {"label": {"fontWeight": 500}}},
            "CodeHighlightTabs": {"styles": {"file": {"padding": 12}}},
            "Table": {
                "defaultProps": {
                    "highlightOnHover": True,
                    "withTableBorder": True,
                    "verticalSpacing": "sm",
                    "horizontalSpacing": "md",
                }
            },
        },
    },
    children=[
        dmc.NotificationProvider(),
        dmc.AppShell(
            [
                dmc.AppShellHeader(dmc.Title(f"Kubedash", order=1), px=25),
                dmc.AppShellNavbar(NavBar()),
                dmc.AppShellMain(dash.page_container),
            ],
            header={"height": 70},
            padding="xl",
            zIndex=1400,
            navbar={
                "width": 250,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
            }
        )
    ],
)

if __name__ == '__main__':
    app.run_server(debug=True)
