import dash
from dash import html, dcc, callback, Input, Output, ctx, ALL
import dash_bootstrap_components as dbc
from dash.dash import PreventUpdate
from dash.html.Button import Button
from kubernetes import client
from datetime import UTC, datetime

dash.register_page(__name__, path='/pods')

v1 = client.CoreV1Api()

def layout():
    return html.Div([
        html.H1('Pods'),
        html.Div(id="pods-list"),
        html.Div(id="pod-info-toast"),
        dcc.Interval(
            id='interval-component',
            interval=10_000, # in milliseconds
            n_intervals=0
        )
    ])

@callback(
    Output("pods-list", "children"),
    Input('interval-component', 'n_intervals')
)
def update_pods_list(n):
    ret = v1.list_pod_for_all_namespaces()

    def format_pod(pod):
        labels = [f"{k}={pod.metadata.labels[k]}" for k in pod.metadata.labels]
        age = datetime.now(UTC) - pod.status.start_time
        return html.Tr([
            html.Td(pod.metadata.namespace),
            html.Td(pod.metadata.name),
            html.Td(", ".join(labels)),
            html.Td(pod.status.phase),
            html.Td(str(age)),
            html.Td(dbc.Button(
                "Delete",
                id={"type": "delete-pod-button", "index": f"{pod.metadata.namespace}/{pod.metadata.name}"},
                n_clicks=0,
                color="danger"
            ))
        ])
    return html.Div(className="table-responsive", children=
        html.Table(className="table table-striped", children=[
            html.Thead(
                html.Tr([
                    html.Th("Namespace"),
                    html.Th("Name"),
                    html.Th("Labels"),
                    html.Th("State"),
                    html.Th("Age"),
                    html.Th(""),
                ])
            ),
            html.Tbody(list(map(format_pod, ret.items)))
        ])
    )

@callback(
    Output("pod-info-toast", "children"),
    Input({"type": "delete-pod-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def delete_pod(n_clicks):
    trigger = ctx.triggered_id
    if not any(n_clicks) or trigger is None:
        # No button was clicked
        raise PreventUpdate
    namespace, pod = trigger['index'].split("/")
    v1.delete_namespaced_pod(pod, namespace)
    toast = dbc.Toast(
        [html.P(f"Deleting pod {pod} in namespace {namespace}", className="mb-0")],
        header="Info",
        icon="info",
        dismissable=True,
        style={"position": "fixed","right": 20, "width": 300},
    )
    return toast
