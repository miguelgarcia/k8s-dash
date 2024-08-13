import dash
from dash import html, dcc, callback, Input, Output, ALL, ctx
from dash.dash import PreventUpdate
import dash_bootstrap_components as dbc
from kubernetes import client
from datetime import UTC, datetime

dash.register_page(__name__, path='/deployments')

v1 = client.AppsV1Api()

def layout():
    return html.Div([
        html.H1('Deployments'),
        html.Div(id="deployments-list"),
        html.Div(id="deployment-info-toast"),
        dcc.Interval(
            id='interval-component',
            interval=10_000, # in milliseconds
            n_intervals=0
        )
    ])

@callback(
    Output("deployments-list", "children"),
    Input('interval-component', 'n_intervals')
)
def update_deployments_list(n):
    ret = v1.list_deployment_for_all_namespaces()
    def format_deployment(d):
        labels = [f"{k}={d.metadata.labels[k]}" for k in d.metadata.labels]
        age = datetime.now(UTC) - d.metadata.creation_timestamp
        return html.Tr([
            html.Td(d.metadata.namespace),
            html.Td(d.metadata.name),
            html.Td([dbc.Badge(x, color="secondary", className="ms-1") for x in labels]),
            html.Td(f"{d.status.available_replicas}/{d.status.replicas}"),
            html.Td(str(age)),
            html.Td(dbc.Button(
                "Restart",
                id={"type": "restart-deployment-button", "index": f"{d.metadata.namespace}/{d.metadata.name}"},
                n_clicks=0,
                color="dark"
            ))
        ])
    return html.Div(className="table-responsive", children=
        html.Table(className="table table-striped", children=[
            html.Thead(
                html.Tr([
                    html.Th("Namespace"),
                    html.Th("Name"),
                    html.Th("Labels"),
                    html.Th("Replicas"),
                    html.Th("Age"),
                    html.Th(""),
                ])
            ),
            html.Tbody(list(map(format_deployment, ret.items)))
        ])
    )


@callback(
    Output("deployment-info-toast", "children"),
    Input({"type": "restart-deployment-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def restart_deployment(n_clicks):
    trigger = ctx.triggered_id
    if not any(n_clicks) or trigger is None:
        # No button was clicked
        raise PreventUpdate
    namespace, deployment = trigger['index'].split("/")
    v1.patch_namespaced_deployment(deployment, namespace, {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt": datetime.now(UTC).isoformat()
                    }
                }
            }
        }
    })
    toast = dbc.Toast(
        [html.P(f"Restarting deployment {deployment} in namespace {namespace}", className="mb-0")],
        header="Info",
        icon="info",
        dismissable=True,
        style={"position": "fixed","right": 20, "width": 300},
    )
    return toast
