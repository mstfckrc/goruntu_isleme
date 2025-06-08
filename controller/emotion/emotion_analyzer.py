from deepface import DeepFace
import numpy as np
from PIL import Image
import io

def analyze_emotion_from_bytes(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_np = np.array(image)
        
        result = DeepFace.analyze(img_np, actions=['emotion'], enforce_detection=False)
        dominant_emotion = result[0]["dominant_emotion"]
        return dominant_emotion
    except Exception as e:
        raise RuntimeError(f"Duygu analizi başarısız: {e}")