from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import torch
import logging
from torchvision import transforms
from model.emotion.model_architecture import create_emotion_model

router = APIRouter()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = create_emotion_model(num_classes=2).to(device)
model.load_state_dict(torch.load("model/emotion/emotion_cnn.pth", map_location=device))
model.eval()

transform = transforms.Compose([
    transforms.Resize((48, 48)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
])

def predict_emotion_from_bytes(image_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = transform(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image)
            _, predicted = torch.max(outputs, 1)
            return "happy" if predicted.item() == 1 else "sad"

    except Exception as e:
        logging.error(f"Duygu tahmini hatası: {e}")
        return "unknown"

@router.post("/api/emotion/")
async def analyze_emotion(file: UploadFile = File(...)):
    image_bytes = await file.read()
    emotion = predict_emotion_from_bytes(image_bytes)
    return {"emotion": emotion}