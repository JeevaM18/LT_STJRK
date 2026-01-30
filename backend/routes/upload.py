from fastapi import APIRouter, UploadFile, File
import networkx as nx

router = APIRouter(prefix="/upload", tags=["Upload"])


# ---------------- GRAPH BUILDER ----------------
def build_graph(symbols, edges):
    G = nx.DiGraph()
    for s in symbols:
        G.add_node(s["id"], **s)
    for e in edges:
        G.add_edge(e["from"], e["to"])
    return G


# ---------------- FEEDER CRITICALITY ----------------
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


# ---------------- RULE ENGINE ----------------
def run_rules(graph):
    risks = []

    feeders = [n for n, d in graph.nodes(data=True) if d["type"] == "FEEDER"]
    breakers = [n for n, d in graph.nodes(data=True) if d["type"] == "BREAKER"]
    transformers = [n for n, d in graph.nodes(data=True) if d["type"] == "TRANSFORMER"]
    loads = [n for n, d in graph.nodes(data=True) if d["type"] == "LOAD"]

    def add_risk(rule, why, symbols, impact, severity, confidence):
        risks.append({
            "rule": rule,
            "why": why,
            "symbols": symbols,
            "impact": impact,
            "severity": severity,
            "confidence": confidence
        })

    # RULE 1: Single feeder
    if len(feeders) == 1:
        add_risk(
            "SINGLE_FEEDER_RISK",
            "Only one feeder exists in the network",
            feeders,
            "Complete outage if feeder fails",
            "HIGH",
            95
        )

    # RULE 2: No backup path
    for f in feeders:
        if graph.out_degree(f) == 1:
            add_risk(
                "NO_BACKUP_PATH",
                f"Feeder {f} has no alternate downstream path",
                [f],
                "Unsafe during maintenance",
                "MEDIUM",
                85
            )

    # RULE 3: Floating breaker
    for b in breakers:
        if graph.out_degree(b) == 0:
            add_risk(
                "FLOATING_BREAKER",
                f"Breaker {b} has no downstream load",
                [b],
                "Broken or incomplete drawing",
                "HIGH",
                94
            )

    # RULE 4: Load without breaker
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

    # RULE 5: Transformer feeds multiple loads
    for t in transformers:
        ds = [d for _, d in graph.edges(t) if graph.nodes[d]["type"] == "LOAD"]
        if len(ds) > 1:
            add_risk(
                "MULTIPLE_LOADS_NO_ISOLATION",
                f"Transformer {t} feeds multiple loads without isolation",
                [t] + ds,
                "Fault propagation risk",
                "MEDIUM",
                85
            )

    return risks


# ---------------- UPLOAD API ----------------
@router.post("/")
async def upload_sld(file: UploadFile = File(...)):

    # 🔁 DEMO EXTRACTION (simulating OCR + CAD)
    symbols = [
        {"id": "S1", "type": "SOURCE", "voltage": "110kV"},
        {"id": "F1", "type": "FEEDER", "voltage": "33kV"},
        {"id": "F2", "type": "FEEDER", "voltage": "33kV"},
        {"id": "B1", "type": "BREAKER"},
        {"id": "B2", "type": "BREAKER"},
        {"id": "T1", "type": "TRANSFORMER"},
        {"id": "L1", "type": "LOAD"},
        {"id": "L2", "type": "LOAD"},
        {"id": "L3", "type": "LOAD"},
    ]

    edges = [
        {"from": "S1", "to": "F1"},
        {"from": "F1", "to": "B1"},
        {"from": "B1", "to": "T1"},
        {"from": "T1", "to": "L1"},
        {"from": "T1", "to": "L2"},
        {"from": "F2", "to": "B2"},
        {"from": "B2", "to": "L3"},
    ]

    graph = build_graph(symbols, edges)
    risks = run_rules(graph)
    criticality = feeder_criticality(graph)

    # GIS DATABASE
    GIS_DB = {
        "F1": {
            "area": "Anna Nagar",
            "polygon": [
                [13.095, 80.275],
                [13.095, 80.285],
                [13.085, 80.285],
                [13.085, 80.275]
            ]
        },
        "F2": {
            "area": "T Nagar",
            "polygon": [
                [13.040, 80.230],
                [13.040, 80.240],
                [13.030, 80.240],
                [13.030, 80.230]
            ]
        }
    }

    affected_feeders = {
        s for r in risks for s in r["symbols"] if s.startswith("F")
    }

    gis = {f: GIS_DB[f] for f in affected_feeders if f in GIS_DB}

    return {
        "symbols": symbols,
        "connectivity": {"edges": edges},
        "risks": risks,
        "why_explainer": risks,
        "criticality": criticality,
        "gis": gis
    }
