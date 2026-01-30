def run_rules(graph):
    risks = []

    def add_risk(rule, why, components, impact, severity, confidence):
        risks.append({
            "rule": rule,
            "why": why,
            "affected_components": components,
            "impact": impact,
            "severity": severity,
            "confidence": confidence
        })

    feeders = [n for n, d in graph.nodes(data=True) if d["type"] == "FEEDER"]
    breakers = [n for n, d in graph.nodes(data=True) if d["type"] == "BREAKER"]
    transformers = [n for n, d in graph.nodes(data=True) if d["type"] == "TRANSFORMER"]
    loads = [n for n, d in graph.nodes(data=True) if d["type"] == "LOAD"]
    sources = [n for n, d in graph.nodes(data=True) if d["type"] == "SOURCE"]

    # 1️⃣ SINGLE FEEDER
    if len(feeders) == 1:
        add_risk(
            "SINGLE_FEEDER_RISK",
            "Only one feeder exists in the network",
            feeders,
            "Complete outage if feeder fails",
            "HIGH",
            95
        )

    # 2️⃣ NO BACKUP PATH
    for f in feeders:
        if graph.out_degree(f) == 1:
            add_risk(
                "NO_BACKUP_PATH",
                f"Feeder {f} has no alternate downstream path",
                [f],
                "Unsafe during maintenance",
                "HIGH",
                90
            )

    # 3️⃣ FLOATING BREAKER
    for b in breakers:
        if graph.out_degree(b) == 0:
            add_risk(
                "FLOATING_BREAKER",
                f"Breaker {b} has no downstream load",
                [b],
                "Broken or incorrect drawing",
                "MEDIUM",
                88
            )

    # 4️⃣ UNCONNECTED EQUIPMENT
    for n in graph.nodes():
        if graph.degree(n) == 0:
            add_risk(
                "UNCONNECTED_EQUIPMENT",
                f"Component {n} is not connected",
                [n],
                "Invalid SLD",
                "HIGH",
                92
            )

    # 5️⃣ LOAD WITHOUT BREAKER
    for l in loads:
        upstream = list(graph.predecessors(l))
        if not any(u in breakers for u in upstream):
            add_risk(
                "LOAD_WITHOUT_BREAKER",
                f"Load {l} is not protected by a breaker",
                [l],
                "Unsafe load connection",
                "HIGH",
                94
            )

    # 6️⃣ TRANSFORMER WITHOUT BREAKER
    for t in transformers:
        upstream = list(graph.predecessors(t))
        if not any(u in breakers for u in upstream):
            add_risk(
                "TRANSFORMER_WITHOUT_BREAKER",
                f"Transformer {t} lacks isolation breaker",
                [t],
                "Unsafe transformer maintenance",
                "HIGH",
                91
            )

    # 7️⃣ FEEDER WITH NO LOAD
    for f in feeders:
        connected_loads = [
            t for _, t in graph.edges(f)
            if graph.nodes[t]["type"] == "LOAD"
        ]
        if len(connected_loads) == 0:
            add_risk(
                "FEEDER_WITH_NO_LOAD",
                f"Feeder {f} is not supplying any load",
                [f],
                "Unused or overdesigned feeder",
                "LOW",
                70
            )

    # 8️⃣ MULTIPLE LOADS WITHOUT ISOLATION
    for t in transformers:
        downstream = [
            d for _, d in graph.edges(t)
            if graph.nodes[d]["type"] == "LOAD"
        ]
        if len(downstream) > 1:
            add_risk(
                "MULTIPLE_LOADS_NO_ISOLATION",
                f"Transformer {t} feeds multiple loads without isolation",
                [t] + downstream,
                "Fault propagation risk",
                "MEDIUM",
                85
            )

    # 9️⃣ DANGLING SOURCE
    for s in sources:
        if graph.out_degree(s) == 0:
            add_risk(
                "DANGLING_SOURCE",
                f"Source {s} is not connected to any feeder",
                [s],
                "Source not utilized",
                "LOW",
                65
            )

    return risks
