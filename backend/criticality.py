def feeder_criticality(graph):
    scores = {}

    for node, data in graph.nodes(data=True):
        if data["type"] == "FEEDER":

            loads = sum(
                1 for _, t in graph.edges(node)
                if graph.nodes[t]["type"] == "LOAD"
            )

            voltage = data.get("voltage", "11kV")
            voltage_score = 3 if "33" in voltage else 1
            backup_penalty = -2 if graph.out_degree(node) == 1 else 0

            score = loads + voltage_score + backup_penalty

            if score >= 6:
                scores[node] = "HIGH"
            elif score >= 3:
                scores[node] = "MEDIUM"
            else:
                scores[node] = "LOW"

    return scores
