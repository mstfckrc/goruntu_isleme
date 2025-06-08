import os
import cv2
from collections import defaultdict
from controller.face.face_recognition_alt import FaceRecognitionAlt

def analyze_recorded_video(video_path):
    model = FaceRecognitionAlt()
    model.load_model()

    video_path = os.path.abspath(os.path.normpath(video_path))  # 🔒 Güvenli ve mutlak yol
    print(f"[VIDEO DEBUG] Analiz edilen video yolu: {video_path}")
    print(f"[EXISTS] {os.path.exists(video_path)}")

    cap = cv2.VideoCapture(video_path)  # 💡 artık tam ve temiz yol
    if not cap.isOpened():
        print("❌ Video açılamadı. Dosya yolu hatalı veya desteklenmeyen format.")
        return {}

    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"[INFO] FPS: {fps}")

    frame_idx = 0
    speaker_frames = defaultdict(int)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        if frame_idx % 5 != 0:
            continue

        boxes, names = model.predict(frame)
        for name in names:
            if name != "Unknown":
                speaker_frames[name] += 1

        print(f"[{frame_idx}] Tanınan: {names}")

    cap.release()
    results = {name: round((count * 5 / fps), 1) for name, count in speaker_frames.items()}
    return results