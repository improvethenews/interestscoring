"""Create an entailment graph based on all the claims for a cluster.
Then, remove all cycles to create a DAG.
Then, order the DAG topologically.
"""
import json

import controversy
import csv
from typing import List, Tuple
from dash import Dash, html
import dash_cytoscape as cyto
import networkx as nx


def get_claim_names(claim_ids: List[int]) -> List[Tuple[int, str]]:
    con, cursor = controversy.get_mysql_connection()
    placeholders = ", ".join(["%s"] * len(claim_ids))
    cursor.execute(
        f"SELECT id, text FROM `claimarticles` "
        f"WHERE `id` IN ({placeholders})",
        claim_ids
    )
    claims = cursor.fetchall()
    return claims  # type: ignore


def update_input():
    cluster = controversy.get_clusters([1])[0]
    claims = controversy.get_claims(cluster[0])
    claim_names = get_claim_names([x for (x,) in claims])
    inferences = controversy.get_inferences([x for (x,) in claims])
    entailments = [x for x in inferences if x[3] == 1]

    # open graph_input/edges.csv and write header row
    with open("graph_input/edges.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["id1", "id2"])
        for entailment in entailments:
            csvwriter.writerow([entailment[1], entailment[2]])

    with open("graph_input/nodes.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["index", "id", "claim"])
        for index, claim in enumerate(claim_names):
            csvwriter.writerow([index + 1, claim[0], claim[1]])


def create_graph():
    graphs = []
    nodes = {}

    # create DAG
    G = nx.DiGraph()
    with open("graph_input/nodes.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            nodes[row[1]] = row[2]
            G.add_node(row[1])

    with open("graph_input/edges.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        for row in csvreader:
            G.add_edge(row[0], row[1])

    # separate into connected components
    for c in sorted(nx.weakly_connected_components(G), key=len, reverse=True):
        graph = G.subgraph(c)
        for node in graph.nodes:
            graph.nodes[node]["label"] = nodes[node]
        graphs.append(graph)

    # remove cycles
    # for graph in graphs:
    #     try:
    #         cycle = list(nx.find_cycle(graph, orientation="ignore"))
    #         print(cycle)
    #     except nx.NetworkXNoCycle:
    #         pass

    # topological sort

    cy_data = nx.cytoscape_data(graphs[0])
    # save to file
    with open("graph_input/graph.json", "w") as jsonfile:
        jsonfile.write(json.dumps(cy_data))


def visualize():
    with open("graph_input/graph.json", "r") as jsonfile:
        cy_data = json.load(jsonfile)

    # import dagre layout
    cyto.load_extra_layouts()

    app = Dash(__name__)
    app.layout = html.Div([
        cyto.Cytoscape(
            id="cytoscape",
            elements=cy_data["elements"],
            layout={"name": "dagre"},
            style={
                "width": "100%",
                "height": "700px",
                "target-arrow-shape": "triangle",
                "target-arrow-color": "black",
                "source-arrow-color": "black",
                "line-color": "#999",
                "curve-style": "bezier"
            },
            maxZoom=2,
            minZoom=0.5,
        )
    ])
    app.run_server(debug=True)


if __name__ == "__main__":
    # update_input()
    create_graph()
