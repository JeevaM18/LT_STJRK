def detect_symbols(image):
    # Mock detections (replace with YOLO later)
    return [
        {"id": "S1", "type": "SOURCE", "x": 50, "y": 50},
        {"id": "F1", "type": "FEEDER", "x": 150, "y": 100},
        {"id": "B1", "type": "BREAKER", "x": 250, "y": 150},
        {"id": "L1", "type": "LOAD", "x": 350, "y": 200}
    ]
