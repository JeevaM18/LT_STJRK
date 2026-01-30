def build_graph(symbols):
    # Sort left → right to infer power flow
    symbols = sorted(symbols, key=lambda s: s["x"])

    nodes = []
    edges = []

    for s in symbols:
        nodes.append({
            "id": s["id"],
            "type": s["type"]
        })

    for i in range(len(symbols) - 1):
        edges.append({
            "from": symbols[i]["id"],
            "to": symbols[i + 1]["id"]
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "power_flow": " → ".join([n["id"] for n in nodes])
    }
