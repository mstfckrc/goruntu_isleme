# controller/face_controller.py

import time
import cv2
import tkinter as tk
from tkinter import messagebox

from globals import get_face_service, set_face_service
from controller.face.face_recognition_service import FaceRecognitionService


def train_face_model():
    """
    Yüz tanıma modeli için eğitim verilerini yükler ve modeli eğitir.
    Başarılı olursa modeli global olarak saklar.
    """
    svc = FaceRecognitionService()
    set_face_service(svc)

    success = svc.train_model()
    if not success:
        messagebox.showerror("Hata", "Yüz tanıma modeli eğitilemedi!")
    return success


def recognize_face(duration: int = 30, max_camera_index: int = 3):
    """
    Canlı webcam akışından yüz tanıma yapar.
    Süre dolana veya 'q' tuşuna basılana kadar çalışır.
    Tanınan kişilerin sürelerini hesaplayıp gösterir.
    """
    svc = get_face_service()
    if svc is None:
        if not train_face_model():
            return
        svc = get_face_service()

    # Kamera seçimi
    cap = None
    for idx in range(max_camera_index + 1):
        temp_cap = cv2.VideoCapture(idx)
        if temp_cap.isOpened():
            cap = temp_cap
            break
        temp_cap.release()

    if cap is None or not cap.isOpened():
        messagebox.showerror(
            "Hata",
            "Kamera açılamadı! Lütfen bir kamera bağlı olduğundan emin olun."
        )
        return

    # Yüz algılama kaskadı
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    start_time = time.time()
    counts = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face_img, (100, 100))

            try:
                ret2, buf = cv2.imencode('.jpg', face_resized)
                if not ret2:
                    raise ValueError("Frame encode edilemedi")
                label = svc.recognize(buf.tobytes())
            except Exception as e:
                print(f"Tanıma hatası: {e}")
                label = None

            if label:
                counts[label] = counts.get(label, 0) + 1
                cv2.putText(
                    frame, label, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2
                )
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

        cv2.imshow('Yüz Tanıma (Çıkmak için q)', frame)

        if (cv2.waitKey(1) & 0xFF == ord('q')) or (time.time() - start_time > duration):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Sonuç gösterimi
    fps_estimate = 30.0
    seconds_per_frame = 1.0 / fps_estimate
    results = [f"{person}: {count * seconds_per_frame:.1f} saniye" for person, count in counts.items()]

    if results:
        messagebox.showinfo("Tanıma Sonuçları", "\n".join(results))
    else:
        messagebox.showwarning("Sonuç", "Hiç yüz tanınamadı.")
