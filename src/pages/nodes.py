"""
Page to view nodes
"""
import dash
from dash import dcc, html, callback, Input, Output
from kubernetes import client
import dash_mantine_components as dmc

dash.register_page(__name__, path="/nodes")

v1 = client.CoreV1Api()
custom_objects = client.CustomObjectsApi()


def layout():
    return html.Div([
        html.H1("Nodes"),
        html.Div(id="nodes-list"),
        html.Div(id="notifications-container"),
        html.Div(id="node-detail"),
        dcc.Interval(
            id="interval-component",
            interval=10_000,
            n_intervals=0
        )
    ])


@callback(
    Output("nodes-list", "children"),
    Input("interval-component", "n_intervals")
)
def update_nodes_list(n):
    ret = v1.list_node()
    for node in ret.items:
        node.status.metrics = {"cpu": "0n", "memory": "0Ki"}
    try:
        stats = custom_objects.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
        for s in stats["items"]:
            for n in ret.items:
                if n.metadata.name == s["metadata"]["name"]:
                    n.status.metrics = s["usage"]
    except Exception as e:
        print(e)

    def format_node(node):
        labels = [f"{k}={node.metadata.labels[k]}" for k in node.metadata.labels]
        addresses = [f"{x.type}: {x.address}" for x in node.status.addresses]
        cpu_usage = (int(node.status.metrics["cpu"].replace("n", "")) / 1_000_000
                     / (int(node.status.capacity["cpu"]) * 1_000))
        memory_usage = (int(node.status.metrics["memory"].replace("Ki", ""))
                        / int(node.status.capacity["memory"].replace("Ki", "")))
        return dmc.TableTr([
            dmc.TableTd(node.metadata.name),
            dmc.TableTd(dmc.Group([dmc.Badge(x, size="sm") for x in labels])),
            dmc.TableTd(dmc.Group([dmc.Badge(x, size="sm") for x in addresses])),
            dmc.TableTd(f"{node.status.allocatable['cpu']} ({cpu_usage:.2%})"),
            dmc.TableTd(f"{node.status.allocatable['memory']} ({memory_usage:.2%})"),
        ])
    return dmc.Table([
        dmc.TableThead(
            dmc.TableTr([
                    dmc.TableTh("Name"),
                    dmc.TableTh("Labels"),
                    dmc.TableTh("IP"),
                    dmc.TableTh("CPU"),
                    dmc.TableTh("RAM"),
            ])
        ),
        dmc.TableTbody(
            list(map(format_node, ret.items))
        )
    ])
