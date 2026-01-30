def check_risks(graph):
    risks = []

    if len(graph["nodes"]) < 2:
        risks.append({
            "type": "INVALID_GRAPH",
            "message": "Not enough components detected"
        })

    feeder_count = len([n for n in graph["nodes"] if n["type"] == "FEEDER"])
    if feeder_count == 1:
        risks.append({
            "type": "SINGLE_FEEDER_RISK",
            "message": "Only one feeder detected — outage risk"
        })

    return risks
