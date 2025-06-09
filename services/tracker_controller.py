import subprocess
import os

process = None

def start_tracker():
    global process
    script = os.path.join("controller", "face", "live_speaker_tracker.py")

    if process is not None:
        if process.poll() is not None:  # Süreç çökmüş
            print("[INFO] Önceki süreç kapanmıştı. Yeni süreç başlatılıyor.")
            process = None
        else:
            return False  # Hâlâ çalışıyor, yeniden başlatma

    process = subprocess.Popen(["python", script])
    print("[INFO] Yeni süreç başlatıldı.")
    return True

# def stop_tracker():
#     global process
#     if process:
#         if process.poll() is None:
#             process.terminate()
#             print("[INFO] Süreç sonlandırıldı.")
#         else:
#             print("[INFO] Süreç zaten durmuş.")
#         process = None
#         try:
#             os.remove("results.json")
#             print("[INFO] results.json dosyası silindi.")
#         except FileNotFoundError:
#             pass
#         return True
#     return False

def stop_tracker():
    global process
    if process and process.poll() is None:  # hâlâ çalışıyorsa
        process.terminate()
        process.wait()  # Sürecin tamamen kapanmasını bekle
        process = None
        print("[INFO] Süreç durduruldu.")
        return True
    print("[INFO] Süreç zaten kapalıydı.")
    return False

def is_tracker_running():
    global process
    return process is not None and process.poll() is None