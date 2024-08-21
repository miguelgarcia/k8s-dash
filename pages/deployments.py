import dash
import yaml
from dash import html, dcc, callback, Input, Output, ctx, ALL
from dash.dash import PreventUpdate
from dash_iconify import DashIconify
from kubernetes import client
from datetime import UTC, datetime
import dash_mantine_components as dmc

dash.register_page(__name__, path='/deployments')

v1 = client.AppsV1Api()


def layout():
    return html.Div([
        html.H1('Deployments'),
        html.Div(id="deployments-list"),
        html.Div(id="notifications-container"),
        html.Div(id="deployment-detail"),
        dcc.Interval(
            id='interval-component',
            interval=10_000,
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
        return dmc.TableTr([
            dmc.TableTd(d.metadata.namespace),
            dmc.TableTd(d.metadata.name),
            dmc.TableTd(dmc.Group([dmc.Badge(x, size="sm") for x in labels])),
            dmc.TableTd(f"{d.status.available_replicas}/{d.status.replicas}"),
            dmc.TableTd(str(age)),
            dmc.TableTd(dmc.Group([
                dmc.ActionIcon(
                    DashIconify(icon="radix-icons:eye-open"),
                    id={
                        "type": "view-deployment-button",
                        "index": f"{d.metadata.namespace}/{d.metadata.name}"
                    },
                    n_clicks=0,
                    color="gray",
                    variant="outline",
                    size="lg",
                ),
                dmc.ActionIcon(
                    DashIconify(icon="radix-icons:symbol"),
                    id={
                        "type": "restart-deployment-button",
                        "index": f"{d.metadata.namespace}/{d.metadata.name}"
                    },
                    n_clicks=0,
                    color="red",
                    variant="filled",
                    size="lg",
                ),
            ]))
        ])
    return dmc.Table([
        dmc.TableThead(
            dmc.TableTr([
                    dmc.TableTh("Namespace"),
                    dmc.TableTh("Name"),
                    dmc.TableTh("Labels", style=dict(width="150px")),
                    dmc.TableTh("Replicas"),
                    dmc.TableTh("Age"),
                    dmc.TableTh(""),
            ])
        ),
        dmc.TableTbody(
            list(map(format_deployment, ret.items))
        )
    ])


@callback(
    Output("notifications-container", "children", allow_duplicate=True),
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
    return dmc.Notification(
        title="Restarting deployment",
        action="show",
        message=f"Restarting deployment {deployment} in namespace {namespace}",
    )


@callback(
    Output("deployment-detail", "children"),
    Input({"type": "view-deployment-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def view_pod(n_clicks):
    trigger = ctx.triggered_id
    if not any(n_clicks) or trigger is None:
        # No button was clicked
        raise PreventUpdate
    namespace, deployment = trigger['index'].split("/")
    podv1 = v1.read_namespaced_deployment(deployment, namespace)
    as_yaml = yaml.dump(v1.api_client.sanitize_for_serialization(podv1), indent=2)
    return dmc.CodeHighlight(as_yaml, language="yaml")
