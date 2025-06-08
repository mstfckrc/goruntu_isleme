import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'controller', 'face')))

from controller.face.face_recognition_alt import FaceRecognitionAlt
from controller.video.analyze_recorded_video import analyze_recorded_video
from controller.video.youtube_downloader import download_with_ytdlp
from controller.video.fix_video import reencode_video  # ✅ ffmpeg destekli dönüştürücü

def main():
    print("📸 Yüz Tanıma Sistemi (face_recognition ile)")
    print("1. Modeli Eğit (dataset klasörü üzerinden)")
    print("2. Kameradan Tanıma Yap")
    print("3. Kayıtlı Video (YouTube) Üzerinden Konuşanları Tanı")
    print("4. Çıkış")

    fr = FaceRecognitionAlt(dataset_dir="data/faces", model_path="encodings.pickle")

    while True:
        choice = input("\nBir seçenek gir (1/2/3/4): ").strip()

        if choice == "1":
            fr.train()

        elif choice == "2":
            fr.recognize_from_camera()

        elif choice == "3":
            url = input("🔗 YouTube video linkini gir: ").strip()
            filename = input("💾 Videoyu hangi isimle kaydetmek istersin? (örnek: konusma.mp4): ").strip()
            if not filename.endswith(".mp4"):
                filename += ".mp4"

            # ⬇ Videoyu indir
            raw_path = download_with_ytdlp(url, filename=filename)
            raw_path = os.path.abspath(os.path.normpath(raw_path))  # Güvenli mutlak yol

            # 🔁 ffmpeg ile yeniden kodla (OpenCV'nin açabileceği format)
            video_path = reencode_video(raw_path)

            # 🧪 DEBUG
            print(f"[FIXED VIDEO PATH] {video_path}")
            print(f"[EXISTS] Dosya mevcut mu? {os.path.exists(video_path)}")

            # ⬇ Analize gönder
            results = analyze_recorded_video(video_path)

            print("\n🧠 Konuşma Süreleri:")
            for name, duration in results.items():
                print(f"👤 {name}: {duration} saniye")

        elif choice == "4":
            print("🚪 Programdan çıkılıyor...")
            break

        else:
            print("⚠️ Geçersiz giriş. Lütfen 1, 2, 3 ya da 4 giriniz.")

if __name__ == "__main__":
    main()

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse, StreamingResponse
# from pydantic import BaseModel
# import subprocess
# import os
# import cv2

# # video analiz fonksiyonları
# from controller.video.youtube_downloader import download_with_ytdlp
# from controller.video.fix_video import reencode_video
# from controller.video.analyze_recorded_video import analyze_recorded_video

# app = FastAPI()

# # CORS ayarı (React için)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # İstersen sadece ["http://localhost:3000"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 🟢 Global subprocess referansı (canlı video için)
# process = None

# @app.post("/api/live/start")
# def start_live_tracker():
#     global process
#     if process is None:
#         try:
#             base_dir = os.getcwd()
#             script_path = os.path.join(base_dir, "controller", "face", "live_speaker_tracker.py")
#             process = subprocess.Popen(
#                 ["python", script_path],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE,
#                 cwd=base_dir
#             )
#             return {"status": "started"}
#         except Exception as e:
#             return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})
#     return {"status": "already_running"}

# @app.post("/api/live/stop")
# def stop_live_tracker():
#     global process
#     if process:
#         process.terminate()
#         process = None
#         return {"status": "stopped"}
#     return {"status": "not_running"}

# # 📽️ Kayıtlı video analizi (User Story 2)
# class VideoRequest(BaseModel):
#     youtube_url: str
#     filename: str

# @app.post("/api/video/analyze")
# def analyze_video(data: VideoRequest):
#     try:
#         raw_path = download_with_ytdlp(data.youtube_url, data.filename)
#         fixed_path = reencode_video(raw_path)
#         results = analyze_recorded_video(fixed_path)
#         return results
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"status": "error", "detail": str(e)})

# # 📡 CANLI KAMERA MJPEG STREAM
# def gen_frames():
#     cap = cv2.VideoCapture(0)
#     if not cap.isOpened():
#         raise RuntimeError("Kamera açılamadı")

#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (
#             b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
#         )

# @app.get("/video_feed")
# def video_feed():
#     return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
