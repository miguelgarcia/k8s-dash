import dash
import dash_auth
import base64
import os
import dash_mantine_components as dmc
from dash import Dash, _dash_renderer, callback, Input, Output, State
from dash_iconify import DashIconify
from kubernetes import config
from components import NavBar

# Required by dmc
_dash_renderer._set_react_version("18.2.0")

config.load_kube_config()

ADMIN_PASSWORD = os.getenv("K8S_DASH_ADMIN_PASSWORD")
if ADMIN_PASSWORD is None:
    raise ValueError("K8S_DASH_ADMIN_PASSWORD must be set")

VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': ADMIN_PASSWORD
}

app = Dash(external_stylesheets=dmc.styles.ALL, use_pages=True, title="k8s-dash")

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS,
    secret_key=base64.b64encode(os.urandom(30)).decode('utf-8')
)

config.load_kube_config()

theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=25), darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
    ],
    variant="transparent",
    color="yellow",
    id="color-scheme-toggle",
    size="lg",
    ms="auto",
)

app.layout = dmc.MantineProvider(
    id="mantine-provider",
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
                dmc.AppShellHeader(
                    dmc.Group([dmc.Title("k8s-dash", order=1), theme_toggle]), px=25
                ),
                dmc.AppShellNavbar([NavBar()]),
                dmc.AppShellMain(dash.page_container),
            ],
            header={"height": 70},
            padding="xl",
            zIndex=1400,
            navbar={
                "width": 250,
                "breakpoint": "sm",
                "collapsed": {"mobile": True},
            },
        ),
    ],
)


@callback(
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-toggle", "n_clicks"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def switch_theme(_, theme):
    return "dark" if theme == "light" else "light"


if __name__ == "__main__":
    app.run_server(debug=False)
