# import os
# from tensorflow.keras.preprocessing.image import ImageDataGenerator
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
# from tensorflow.keras.optimizers import Adam

# def train_emotion_model(data_dir="data/emotion", save_path="model/emotion/emotion_model.h5"):
#     img_size = 48
#     batch_size = 2

#     datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

#     train_generator = datagen.flow_from_directory(
#         data_dir,
#         target_size=(img_size, img_size),
#         batch_size=batch_size,
#         class_mode='categorical',
#         subset='training'
#     )

#     val_generator = datagen.flow_from_directory(
#         data_dir,
#         target_size=(img_size, img_size),
#         batch_size=batch_size,
#         class_mode='categorical',
#         subset='validation'
#     )

#     model = Sequential([
#         Conv2D(32, (3,3), activation='relu', input_shape=(img_size, img_size, 3)),
#         MaxPooling2D(2,2),
#         Conv2D(64, (3,3), activation='relu'),
#         MaxPooling2D(2,2),
#         Flatten(),
#         Dense(64, activation='relu'),
#         Dense(2, activation='softmax')
#     ])

#     model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

#     model.fit(train_generator, validation_data=val_generator, epochs=15)

#     os.makedirs(os.path.dirname(save_path), exist_ok=True)
#     model.save(save_path)
#     print(f"[EĞİTİM] Model başarıyla kaydedildi: {save_path}")

# if __name__ == "__main__":
#         print("🚀 Eğitim başlatılıyor...")
#         train_emotion_model()

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report
from model.emotion.model_architecture import create_emotion_model

# ✅ Klasörler
data_dir = "data/emotion"
model_save_path = "model/emotion/emotion_cnn.pth"

# ✅ Donanım
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ✅ Veriler
transform = transforms.Compose([
    transforms.Resize((48, 48)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.Grayscale(num_output_channels=3),  # RGB yerine gri
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5]),  # Eğer eğitimde normalize varsa testte de olacak
])

dataset = datasets.ImageFolder(data_dir, transform=transform)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size
train_ds, val_ds = torch.utils.data.random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_ds, batch_size=8, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=8)

# ✅ Modeli oluştur (dış dosyadan çağır)
model = create_emotion_model(num_classes=len(dataset.classes)).to(device)

# ✅ Eğitim
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

epochs = 15
for epoch in range(epochs):
    model.train()
    total_loss = 0
    for imgs, labels in train_loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/{epochs} | Loss: {total_loss:.4f}")

# ✅ Doğrulama
model.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for imgs, labels in val_loader:
        imgs = imgs.to(device)
        outputs = model(imgs)
        preds = torch.argmax(outputs, dim=1).cpu()
        y_true.extend(labels.numpy())
        y_pred.extend(preds.numpy())

print("🔍 Doğruluk Sonuçları:\n", classification_report(y_true, y_pred, target_names=dataset.classes))

# ✅ Kaydet
os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
torch.save(model.state_dict(), model_save_path)
print(f"✅ Model kaydedildi: {model_save_path}")