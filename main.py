# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'controller', 'face')))

# from controller.face.face_recognition_alt import FaceRecognitionAlt
# from controller.video.analyze_recorded_video import analyze_recorded_video
# from controller.video.youtube_downloader import download_with_ytdlp
# from controller.video.fix_video import reencode_video  # ✅ ffmpeg destekli dönüştürücü

# def main():
#     print("📸 Yüz Tanıma Sistemi (face_recognition ile)")
#     print("1. Modeli Eğit (dataset klasörü üzerinden)")
#     print("2. Kameradan Tanıma Yap")
#     print("3. Kayıtlı Video (YouTube) Üzerinden Konuşanları Tanı")
#     print("4. Çıkış")

#     fr = FaceRecognitionAlt(dataset_dir="data/faces", model_path="encodings.pickle")

#     while True:
#         choice = input("\nBir seçenek gir (1/2/3/4): ").strip()

#         if choice == "1":
#             fr.train()

#         elif choice == "2":
#             fr.recognize_from_camera()

#         elif choice == "3":
#             url = input("🔗 YouTube video linkini gir: ").strip()
#             filename = input("💾 Videoyu hangi isimle kaydetmek istersin? (örnek: konusma.mp4): ").strip()
#             if not filename.endswith(".mp4"):
#                 filename += ".mp4"

#             # ⬇ Videoyu indir
#             raw_path = download_with_ytdlp(url, filename=filename)
#             raw_path = os.path.abspath(os.path.normpath(raw_path))  # Güvenli mutlak yol

#             # 🔁 ffmpeg ile yeniden kodla (OpenCV'nin açabileceği format)
#             video_path = reencode_video(raw_path)

#             # 🧪 DEBUG
#             print(f"[FIXED VIDEO PATH] {video_path}")
#             print(f"[EXISTS] Dosya mevcut mu? {os.path.exists(video_path)}")

#             # ⬇ Analize gönder
#             results = analyze_recorded_video(video_path)

#             print("\n🧠 Konuşma Süreleri:")
#             for name, duration in results.items():
#                 print(f"👤 {name}: {duration} saniye")

#         elif choice == "4":
#             print("🚪 Programdan çıkılıyor...")
#             break

#         else:
#             print("⚠️ Geçersiz giriş. Lütfen 1, 2, 3 ya da 4 giriniz.")

# if __name__ == "__main__":
#     main()


from collections import defaultdict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import subprocess
import os
import json
# 📁 Video analiz modülleri (User Story 2)
from controller.video.youtube_downloader import download_with_ytdlp
from controller.video.fix_video import reencode_video
from controller.video.analyze_recorded_video import analyze_recorded_video
from fastapi import FastAPI
from routers import video

app = FastAPI()

app.include_router(video.router)

# 🌐 CORS ayarları (React frontend ile bağlantı için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Gerekirse sadece ["http://localhost:3000"] yaz
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔁 Global subprocess referansı (canlı izleme için)
process = None

@app.post("/api/live/start")
def start_live_tracker():
    global process
    if process is None:
        try:
            base_dir = os.getcwd()
            script_path = os.path.join(base_dir, "controller", "face", "live_speaker_tracker.py")
            process = subprocess.Popen(
                ["python", script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=base_dir
            )
            return {"status": "started"}
        except Exception as e:
            return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})
    return {"status": "already_running"}

@app.post("/api/live/stop")
def stop_live_tracker():
    global process
    if process:
        process.terminate()
        process = None
        return {"status": "stopped"}
    return {"status": "not_running"}

@app.get("/api/live/results")
def get_live_results():
    try:
        with open("results.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}


@app.get("/api/live/status")
def live_status():
    return {"running": process is not None}

# 📽️ Kayıtlı video analizi (User Story 2)
class VideoRequest(BaseModel):
    youtube_url: str
    filename: str

@app.post("/api/video/analyze")
def analyze_video(data: VideoRequest):
    try:
        raw_path = download_with_ytdlp(data.youtube_url, data.filename)
        fixed_path = reencode_video(raw_path)
        result = analyze_recorded_video(fixed_path)
        return result
    except Exception as e:
        print(f"[BACKEND HATA] {e}")
        return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

speaking_times = defaultdict(float)
last_spoken = defaultdict(float)

def gen_frames():
    import cv2
    import face_recognition
    import sounddevice as sd
    import numpy as np
    import pickle
    import time
    import librosa
    import json
    from scipy.spatial.distance import cosine

    global speaking_times, last_spoken

    # Modelleri yükle
    with open("encodings.pickle", "rb") as f:
        face_model = pickle.load(f)
    known_encodings = face_model["encodings"]
    known_names = face_model["names"]

    with open("voice_encodings.pickle", "rb") as f:
        voice_model = pickle.load(f)
    voice_encodings = voice_model["encodings"]
    voice_names = voice_model["names"]

    print(f"[SES MODELİ] {len(voice_names)} ses kaydı yüklendi.")

    def extract_mfcc(audio, sr):
        audio = audio.astype(np.float32) / np.max(np.abs(audio))
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        return np.mean(mfcc.T, axis=0)

    def identify_speaker_by_voice(audio, sr):
        mfcc_vector = extract_mfcc(audio, sr)
        similarities = [1 - cosine(mfcc_vector, v) for v in voice_encodings]
        if not similarities:
            return None
        best_match_idx = int(np.argmax(similarities))
        return voice_names[best_match_idx]

    def is_speaker_confident(audio, sr, expected_name, threshold=0.85):
        mfcc_vector = extract_mfcc(audio, sr)
        similarities = [(1 - cosine(mfcc_vector, v), n) for v, n in zip(voice_encodings, voice_names)]
        relevant_scores = [sim for sim, name in similarities if name == expected_name]
        return len(relevant_scores) > 0 and max(relevant_scores) > threshold

    def get_volume_level(duration=0.5, fs=44100):
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        volume_norm = np.linalg.norm(recording) / len(recording)
        return volume_norm, recording.flatten(), fs


    start_time = time.time()
    volume_threshold = 1.0

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("Kamera açılamadı")

    while True:
        success, frame = cap.read()
        if not success:
            break

        current_time = time.time()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        volume, audio_data, sr = get_volume_level()
        speaker_predicted = identify_speaker_by_voice(audio_data, sr)
        print(f"[SES] Tahmin: {speaker_predicted} | Ses şiddeti: {volume:.3f}")

        for (top, right, bottom, left), encoding in zip(boxes, encodings):
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            name = "Bilinmiyor"
            if True in matches:
                matched_idxs = [i for i, b in enumerate(matches) if b]
                counts = {}
                for i in matched_idxs:
                    counts[known_names[i]] = counts.get(known_names[i], 0) + 1
                name = max(counts, key=counts.get)

            if name != "Bilinmiyor" and speaker_predicted == name and volume > volume_threshold:
                if is_speaker_confident(audio_data, sr, speaker_predicted):
                    elapsed = current_time - last_spoken.get(name, current_time)
                    if elapsed < 1.5:
                        speaking_times[name] += elapsed
                    last_spoken[name] = current_time
                    print(f"[KONUŞMA] {name} +{elapsed:.2f} sn eklendi")

            label = f"{name}"
            if speaker_predicted == name and volume > volume_threshold:
                label += " ✅"
            elif name != "Bilinmiyor":
                label += " 🔇"

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        with open("results.json", "w", encoding="utf-8") as f:
            json.dump({name: int(s) for name, s in speaking_times.items()}, f, ensure_ascii=False, indent=2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
        )

    cap.release()


@app.get("/video_feed")
def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# @app.get("/api/live/results")
# def get_live_results():
#     try:
#         with open("results.json", "r", encoding="utf-8") as f:
#             data = json.load(f)
#         return data
#     except FileNotFoundError:
#         return {}

@app.get("/api/live/results")
def get_results():
    global speaking_times
    return {name: round(s, 2) for name, s in speaking_times.items()}

@app.get("/")
def index():
    return {"message": "🎯 Sistem aktif"}
