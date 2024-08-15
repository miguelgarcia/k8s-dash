import dash
import yaml
from dash import html, dcc, callback, Input, Output, ctx, ALL
from dash.dash import PreventUpdate
from dash.html.Button import Button
from kubernetes import client
from datetime import UTC, datetime
import dash_mantine_components as dmc

dash.register_page(__name__, path='/pods')

v1 = client.CoreV1Api()

def layout():
    return html.Div([
        html.H1('Pods'),
        html.Div(id="pods-list"),
        html.Div(id="notifications-container"),
        html.Div(id="pod-detail"),
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
        return dmc.TableTr([
            dmc.TableTd(pod.metadata.namespace),
            dmc.TableTd(pod.metadata.name),
            dmc.TableTd(dmc.Group([dmc.Badge(x, size="sm") for x in labels])),
            dmc.TableTd(pod.status.phase),
            dmc.TableTd(str(age)),
            dmc.TableTd(dmc.Group([
                dmc.Button(
                    "View",
                    id={"type": "view-pod-button", "index": f"{pod.metadata.namespace}/{pod.metadata.name}"},
                    n_clicks=0,
                    size="sm",
                ),
                dmc.Button(
                    "Delete",
                    id={"type": "delete-pod-button", "index": f"{pod.metadata.namespace}/{pod.metadata.name}"},
                    n_clicks=0,
                    color="red",
                    size="sm",
                )
            ]))
        ])
    return dmc.Table([
        dmc.TableThead(
            dmc.TableTr([
                    dmc.TableTh("Namespace"),
                    dmc.TableTh("Name"),
                    dmc.TableTh("Labels"),
                    dmc.TableTh("State"),
                    dmc.TableTh("Age"),
                    dmc.TableTh(""),
            ])
        ),
        dmc.TableTbody(
            list(map(format_pod, ret.items))
        )
    ])

@callback(
    Output("pod-detail", "children"),
    Input({"type": "view-pod-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def view_pod(n_clicks):
    trigger = ctx.triggered_id
    if not any(n_clicks) or trigger is None:
        # No button was clicked
        raise PreventUpdate
    namespace, pod = trigger['index'].split("/")
    podv1 = v1.read_namespaced_pod(pod, namespace)
    as_yaml = yaml.dump(v1.api_client.sanitize_for_serialization(podv1), indent=2)
    return dmc.CodeHighlight(as_yaml, language="yaml")

@callback(
    Output("notifications-container", "children", allow_duplicate=True),
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
    return dmc.Notification(
        title="Deleting pod",
        action="show",
        message=f"Deleting pod {pod} in namespace {namespace}",
    )
