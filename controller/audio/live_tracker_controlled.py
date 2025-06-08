from flask import Flask, Response, jsonify
from flask_cors import CORS  # ✅ CORS buraya ekleniyor
import cv2
import face_recognition
import pickle
import time
import threading
import sounddevice as sd
import numpy as np
from collections import defaultdict

app = Flask(__name__)
CORS(app)

# Model yükle
with open("encodings.pickle", "rb") as f:
    model_data = pickle.load(f)
known_encodings = model_data["encodings"]
known_names = model_data["names"]

# Global değişkenler
tracking_active = False
tracking_thread = None
speaking_times = defaultdict(float)
last_spoken = defaultdict(float)
frame_buffer = None
start_time = None
volume_threshold = 0.02
MAX_DURATION = 60  # Otomatik durma süresi



def get_volume_level(duration=0.4, fs=44100):
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        volume_norm = np.linalg.norm(recording) / len(recording)
        return volume_norm
    except:
        return 0.0
    
def track_faces():
    global tracking_active, frame_buffer, speaking_times, last_spoken, start_time

    print("[TRACK] track_faces başladı.")
    cap = cv2.VideoCapture(0)
    print(f"[KAMERA] Açıldı mı? {cap.isOpened()}")  # terminalde göreceksin

    if not cap.isOpened():
        print("❌ Kamera başlatılamadı.")
        tracking_active = False
        return

    start_time = time.time()
    while tracking_active:
        ret, frame = cap.read()
        print("[KAMERA] Frame alındı:", ret)
        if not ret:
            continue

        current_time = time.time()
        elapsed_total = int(current_time - start_time)
        if elapsed_total > MAX_DURATION:
            print("⏱ 60 saniye doldu. Otomatik durduruluyor.")
            tracking_active = False
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        detected_names = []

        for (top, right, bottom, left), encoding in zip(boxes, encodings):
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            name = "Bilinmiyor"
            if True in matches:
                matched_idxs = [i for i, b in enumerate(matches) if b]
                counts = {}
                for i in matched_idxs:
                    counts[known_names[i]] = counts.get(known_names[i], 0) + 1
                name = max(counts, key=counts.get)
            detected_names.append(name)

            volume = get_volume_level()
            if name != "Bilinmiyor" and volume > volume_threshold:
                elapsed = current_time - last_spoken.get(name, current_time)
                if elapsed < 1.5:
                    speaking_times[name] += elapsed
                last_spoken[name] = current_time

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        y = 30
        cv2.putText(frame, f"Geçen süre: {elapsed_total} sn", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        y += 30
        for name, duration in speaking_times.items():
            text = f"{name}: {int(duration)} sn"
            cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            y += 25

        _, buffer = cv2.imencode('.jpg', frame)
        frame_buffer = buffer.tobytes()
        print("[FRAME] Yeni frame alındı ve buffer'a yazıldı.")

        time.sleep(0.04)

    cap.release()
    print("📷 Kamera serbest bırakıldı.")


@app.route("/start", methods=["POST"])
def start_tracking():
    global tracking_active, tracking_thread, speaking_times, last_spoken
    if not tracking_active:
        print("📡 Takip başlatıldı.")
        speaking_times.clear()
        last_spoken.clear()
        tracking_active = True
        tracking_thread = threading.Thread(target=track_faces)
        tracking_thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})

@app.route("/stop", methods=["POST"])
def stop_tracking():
    global tracking_active
    tracking_active = False
    time.sleep(1)  # Kamera kapanana kadar bekle
    return jsonify(dict(speaking_times))

@app.route("/video_feed")
def video_feed():
    print("[STREAM] /video_feed çağrıldı.")
    
    def generate():
        while True:
            if tracking_active and frame_buffer:
                print("[STREAM] Frame gönderiliyor...")
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n'
                )
            else:
                # Kamera başlamamışsa boş frame gönder (1x1 pixel)
                import numpy as np
                import cv2
                dummy = np.zeros((1, 1, 3), dtype=np.uint8)
                _, buf = cv2.imencode('.jpg', dummy)
                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + buf.tobytes() + b'\r\n'
                )
            time.sleep(0.05)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return "🧠 Flask Kamera Takip Servisi Aktif."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
