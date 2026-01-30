def sld_output_schema(symbols, graph, risks):
    return {
        "symbols": symbols,
        "connectivity": graph,
        "risks": risks
    }
