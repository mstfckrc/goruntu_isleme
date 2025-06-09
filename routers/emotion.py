import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from io import BytesIO
import os
import sys

# Yol ayarı (model.emotion.model_architecture'a ulaşmak için)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from model.emotion.model_architecture import create_emotion_model

router = APIRouter()

# ✅ Model yükle
model_path = "model/emotion/emotion_cnn.pth"
model = create_emotion_model(num_classes=2)
model.load_state_dict(torch.load(model_path, map_location="cpu"))
model.eval()

# ✅ Görsel dönüştürücü (grayscale + resize + tensor)
transform = transforms.Compose([
    transforms.Grayscale(),
    transforms.Resize((48, 48)),
    transforms.ToTensor()
])

@router.post("/api/emotion/")
async def analyze_emotion(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents)).convert("RGB")
        image = transform(image).unsqueeze(0)

        with torch.no_grad():
            output = model(image)
            prediction = torch.argmax(F.softmax(output, dim=1), dim=1).item()

        label = "happy_emotion" if prediction == 0 else "sad_emotion"
        return {"emotion": label}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})