import dash
from dash import html, dcc, callback, Input, Output
from kubernetes import client
from datetime import UTC, datetime

dash.register_page(__name__, path='/pods')

v1 = client.CoreV1Api()

def layout():
    return html.Div([
        html.H1('Pods'),
        html.Div(id="pods-list"),
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
            html.Td(str(age))
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
                ])
            ),
            html.Tbody(list(map(format_pod, ret.items)))
        ])
    )
