# controller/face_recognition_service.py

import cv2
import numpy as np
import os
from pathlib import Path

class FaceRecognitionService:
    def __init__(self):
        # Proje kökünü __file__ ila bul
        file_path   = Path(__file__).resolve()
        project_root = file_path.parent.parent.parent

        # Yüz fotoğrafları: data/faces/{kişi}/...
        self.data_path = project_root / "data" / "faces"

        # Cascade yükle
        self.face_detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        # LBPH tanıyıcı oluştur
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        # Eğitim sonrası tutulacak harita
        self.label_map = {}

    def train_model(self):
        """
        Her çağrıda data/faces altındaki tüm kişi klasörlerindeki
        JPG/PNG dosyalarından modeli eğitir. Dosyaya yazma yok.
        """
        images, labels = [], []
        self.label_map.clear()
        current_label = 0

        if not self.data_path.exists():
            return False

        for person_dir in self.data_path.iterdir():
            if not person_dir.is_dir():
                continue
            current_label += 1
            self.label_map[current_label] = person_dir.name

            for img_path in person_dir.glob("*"):
                if img_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                    continue
                # Byte’dan görüntüye
                data = img_path.read_bytes()
                nparr = np.frombuffer(data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                faces = self.face_detector.detectMultiScale(img, 1.1, 4)
                if len(faces) == 0:
                    continue
                x,y,w,h = faces[0]
                face = cv2.resize(img[y:y+h, x:x+w], (100, 100))
                images.append(face)
                labels.append(current_label)

        if not images:
            return False

        # Eğit
        self.recognizer.train(images, np.array(labels))

        print(f"[EĞİTİM TAMAMLANDI] label_map: {self.label_map}")

        return True

    def recognize(self, image_bytes):
        """
        Verilen JPG/PNG byte dizisinden yüzü tespit eder,
        modelle tahmin yapar ve kişi adını döner.
        """
        # Görüntü decode
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        faces = self.face_detector.detectMultiScale(img, 1.1, 4)
        if len(faces) == 0:
            return None

        x,y,w,h = faces[0]
        face = cv2.resize(img[y:y+h, x:x+w], (100, 100))

        try:
            label, confidence = self.recognizer.predict(face)
            print(f"➡️ Predict sonucu: label={label}, confidence={confidence}")
            print(f"➡️ Haritadaki isim: {self.label_map.get(label)}")
        except Exception:
            return None

        # Eşik kontrolü: low distance = high confidence
        if label > 0 and confidence < 200:
            return self.label_map.get(label)
        return None
