import torch.nn as nn
from torchvision import models

def create_emotion_model(num_classes=2):
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model