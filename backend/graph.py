import networkx as nx

def build_graph(symbols, edges):
    G = nx.DiGraph()

    for s in symbols:
        G.add_node(s["id"], **s)

    for e in edges:
        G.add_edge(e["from"], e["to"])

    return G
