import numpy as np
import cv2

from services.symbol_detector import detect_symbols
from services.ocr_reader import read_text
from services.graph_builder import build_graph
from services.risk_checker import check_risks
from utils.image_utils import load_image

def process_sld(file):
    image = load_image(file)

    symbols = detect_symbols(image)
    text_data = read_text(image)
    graph = build_graph(symbols)
    risks = check_risks(graph)

    return {
        "symbols": symbols,
        "text": text_data,
        "connectivity": graph,
        "risks": risks
    }
