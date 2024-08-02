import dash
from dash import html, dcc, callback, Input, Output
from kubernetes import client
from datetime import UTC, datetime

dash.register_page(__name__, path='/deployments')

v1 = client.AppsV1Api()

def layout():
    return html.Div([
        html.H1('Deployments'),
        html.Div(id="deployments-list"),
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
            html.Td(", ".join(labels)),
            html.Td(f"{d.status.available_replicas}/{d.status.replicas}"),
            html.Td(str(age))
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
                ])
            ),
            html.Tbody(list(map(format_deployment, ret.items)))
        ])
    )
