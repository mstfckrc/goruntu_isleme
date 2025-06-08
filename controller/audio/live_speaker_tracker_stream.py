from flask import Flask, Response, jsonify
from flask_cors import CORS  # ✅ CORS buraya ekleniyor
import cv2
import face_recognition
import pickle
import time
import threading
import numpy as np
import sounddevice as sd
from collections import defaultdict

app = Flask(__name__)
CORS(app) 

# 📁 Model yükle
with open("encodings.pickle", "rb") as f:
    model_data = pickle.load(f)
known_encodings = model_data["encodings"]
known_names = model_data["names"]

speaking_times = defaultdict(float)
last_spoken = defaultdict(float)
start_time = time.time()

tracking_active = False

# 🔊 Ses eşiği
volume_threshold = 0.02

# 📷 Kamera başlat
cap = cv2.VideoCapture(0)

def get_volume_level(duration=0.4, fs=44100):
    """Mikrofondan gelen sesin yoğunluğunu ölç."""
    try:
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        volume_norm = np.linalg.norm(recording) / len(recording)
        return volume_norm
    except Exception as e:
        print("[SES HATASI]", str(e))
        return 0.0
    
def generate_frames():
    global speaking_times, last_spoken, start_time, tracking_active

    while True:
        if not tracking_active:
            time.sleep(0.1)
            continue

        elapsed = time.time() - start_time
        if elapsed > 1000:
            print("⏱ Maksimum süre doldu, takip durduruluyor.")
            tracking_active = False
            continue

        success, frame = cap.read()
        if not success:
            print("⚠️ Kamera okunamadı, yeniden deneniyor...")
            time.sleep(0.5)
            continue  # ❗ stream kesilmesin, kamera kendine gelince devam et

        current_time = time.time()
        elapsed_total = int(current_time - start_time)

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

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

@app.route("/start", methods=["POST"])
def start_tracking():
    global tracking_active, tracking_thread, speaking_times, last_spoken, cap

    if 'tracking_active' not in globals():
        tracking_active = False
    if 'tracking_thread' not in globals():
        tracking_thread = None

    if tracking_active:
        tracking_active = False
        if tracking_thread and tracking_thread.is_alive():
            tracking_thread.join()
        cap.release()
        cap = cv2.VideoCapture(0)

    print("📡 Takip yeniden başlatılıyor.")
    speaking_times.clear()
    last_spoken.clear()
    tracking_active = True

    def track_faces():
        for _ in generate_frames():
            if not tracking_active:
                break

    tracking_thread = threading.Thread(target=track_faces)
    tracking_thread.start()

    return jsonify({"status": "restarted"})

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/")
def index():
    return "🧠 Flask Kamera Yayını Aktif - /video_feed adresine gidin."

@app.route("/result")
def get_speaking_results():
    global tracking_active
    if not tracking_active:
        return jsonify({"status": "timeout", "results": dict(speaking_times)})
    return jsonify({name: int(duration) for name, duration in speaking_times.items()})

@app.route("/stop", methods=["POST"])
def stop_tracking():
    global tracking_active
    tracking_active = False
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

