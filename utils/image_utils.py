import numpy as np
import cv2

def load_image(file):
    image_bytes = file.file.read()
    img_array = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    return image
