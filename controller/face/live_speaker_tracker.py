# import cv2
# import face_recognition
# import sounddevice as sd
# import numpy as np
# import pickle
# import time
# from collections import defaultdict

# class LiveSpeakerTracker:
#     def __init__(self, model_path="encodings.pickle", frame_skip=5):
#         self.model_path = model_path
#         self.known_encodings = []
#         self.known_names = []
#         self.speaking_times = defaultdict(float)
#         self.current_speaker = None
#         self.frame_skip = frame_skip
#         self.frame_count = 0
#         self.last_speaker_time = time.time()
#         self.volume_threshold = 0.03  # ayarlanabilir

#     def load_model(self):
#         with open(self.model_path, "rb") as f:
#             data = pickle.load(f)
#             self.known_encodings = data["encodings"]
#             self.known_names = data["names"]
#         print(f"[MODEL] {len(self.known_names)} kişi yüklendi.")

#     def get_volume_level(self, duration=0.1, fs=44100):
#         recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)
#         volume_norm = np.linalg.norm(recording) / len(recording)
#         return volume_norm

#     def start_tracking(self):
#         self.load_model()
#         cap = cv2.VideoCapture(0)

#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break

#             self.frame_count += 1
#             speaker_candidate = None

#             if self.frame_count % self.frame_skip == 0:
#                 rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#                 boxes = face_recognition.face_locations(rgb)
#                 encodings = face_recognition.face_encodings(rgb, boxes)

#                 for (top, right, bottom, left), encoding in zip(boxes, encodings):
#                     matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.5)
#                     name = "Bilinmiyor"
#                     if True in matches:
#                         matched_idxs = [i for i, b in enumerate(matches) if b]
#                         counts = {}
#                         for i in matched_idxs:
#                             counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1
#                         name = max(counts, key=counts.get)

#                     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
#                     cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

#                     speaker_candidate = name

#             volume = self.get_volume_level()
#             if volume > self.volume_threshold and speaker_candidate:
#                 now = time.time()
#                 elapsed = now - self.last_speaker_time
#                 self.speaking_times[speaker_candidate] += elapsed
#                 self.last_speaker_time = now
#                 self.current_speaker = speaker_candidate

#             # Görselde süreleri yaz
#             y_offset = 30
#             for name, duration in self.speaking_times.items():
#                 text = f"{name}: {int(duration)} sn"
#                 cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
#                 y_offset += 25

#             cv2.imshow("Canlı Konuşan Takibi", frame)
#             if cv2.waitKey(1) & 0xFF == ord("q"):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

#         print("\nKonuşma Süreleri:")
#         for name, duration in self.speaking_times.items():
#             print(f"{name}: {int(duration)} saniye")


# if __name__ == "__main__":
#     tracker = LiveSpeakerTracker()
#     tracker.start_tracking()

import cv2
import face_recognition
import sounddevice as sd
import numpy as np
import pickle
import time
import librosa
from collections import defaultdict
from scipy.spatial.distance import cosine

class LiveSpeakerTracker:
    def __init__(self, model_path="encodings.pickle", voice_model_path="voice_encodings.pickle", frame_skip=5):
        self.model_path = model_path
        self.voice_model_path = voice_model_path
        self.known_encodings = []
        self.known_names = []
        self.voice_encodings = []
        self.voice_names = []
        self.speaking_times = defaultdict(float)
        self.current_speaker = None
        self.frame_skip = frame_skip
        self.frame_count = 0
        self.volume_threshold = 1.0
        self.max_duration = 60

    def predict_from_audio(self, audio, sr):
        mfcc_vector = self.extract_mfcc(audio, sr)
        similarities = [1 - cosine(mfcc_vector, v) for v in self.voice_encodings]
        if not similarities:
            return None
        best_match_idx = int(np.argmax(similarities))
        name = self.voice_names[best_match_idx]
        confidence = similarities[best_match_idx]
        return name if confidence > 0.85 else None

    def load_model(self):
        with open(self.model_path, "rb") as f:
            data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_names = data["names"]
        print(f"[MODEL] {len(self.known_names)} kişi yüklendi.")

    def load_voice_model(self):
        with open(self.voice_model_path, "rb") as f:
            data = pickle.load(f)
            self.voice_encodings = data["encodings"]
            self.voice_names = data["names"]
        print(f"[SES MODELİ] {len(self.voice_names)} ses kaydı yüklendi.")

    def get_volume_level(self, duration=0.5, fs=44100):
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        volume_norm = np.linalg.norm(recording) / len(recording)
        return volume_norm, recording.flatten(), fs

    def extract_mfcc(self, audio, sr):
        audio = audio.astype(np.float32) / np.max(np.abs(audio))
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        return np.mean(mfcc.T, axis=0)

    def identify_speaker_by_voice(self, audio, sr):
        mfcc_vector = self.extract_mfcc(audio, sr)
        similarities = [1 - cosine(mfcc_vector, v) for v in self.voice_encodings]
        if not similarities:
            return None
        best_match_idx = int(np.argmax(similarities))
        voice_name = self.voice_names[best_match_idx]
        print(f"[SES EŞLEŞME] {voice_name}")
        return voice_name

    def is_speaker_confident(self, audio, sr, expected_name, threshold=0.85):
        mfcc_vector = self.extract_mfcc(audio, sr)
        similarities = [(1 - cosine(mfcc_vector, v), n) for v, n in zip(self.voice_encodings, self.voice_names)]
        relevant_scores = [sim for sim, name in similarities if name == expected_name]
        return len(relevant_scores) > 0 and max(relevant_scores) > threshold

    def start_tracking(self):
        self.start_time = time.time()
        self.last_speaker_time = time.time()
        self.load_model()
        self.load_voice_model()
        cap = cv2.VideoCapture(0)

        while True:
            elapsed_total = time.time() - self.start_time
            if elapsed_total > self.max_duration:
                print("\n⏱ Maksimum izleme süresi doldu (60 saniye). Çıkılıyor...")
                break

            ret, frame = cap.read()
            if not ret:
                break

            self.frame_count += 1
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)
            detected_names = []

            for (top, right, bottom, left), encoding in zip(boxes, encodings):
                matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.5)
                name = "Bilinmiyor"
                if True in matches:
                    matched_idxs = [i for i, b in enumerate(matches) if b]
                    counts = {}
                    for i in matched_idxs:
                        counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1
                    name = max(counts, key=counts.get)
                detected_names.append(name)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            volume, audio_data, sr = self.get_volume_level()
            print(f"[SES ŞİDDETİ] {volume:.4f}")
            if volume > self.volume_threshold:
                voice_name = self.identify_speaker_by_voice(audio_data, sr)
                if voice_name and self.is_speaker_confident(audio_data, sr, voice_name):
                    print(f"[ALGILANAN] {voice_name} konuşuyor olabilir.")
                    if voice_name in detected_names:
                        now = time.time()
                        elapsed = now - self.last_speaker_time
                        if elapsed < 2.0:  # Uzun sessizlik varsa sayma
                            self.speaking_times[voice_name] += elapsed
                        self.last_speaker_time = now
                        self.current_speaker = voice_name
            else:
                self.last_speaker_time = time.time()  # Sessizlik varsa zaman sıfırla

            y_offset = 30
            cv2.putText(frame, f"Geçen süre: {int(elapsed_total)} sn", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_offset += 30
            for name, duration in self.speaking_times.items():
                text = f"{name}: {int(duration)} sn"
                cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_offset += 25

            cv2.imshow("Canlı Konuşan Takibi", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


        print("\nKonuşma Süreleri:")
        for name, duration in self.speaking_times.items():
            print(f"{name}: {int(duration)} saniye")


if __name__ == "__main__":
    tracker = LiveSpeakerTracker()
    tracker.start_tracking()


# import face_recognition
# import cv2
# import numpy as np
# import sounddevice as sd
# import pickle
# import time
# import json
# from collections import defaultdict
# import librosa

# # 📁 Yüz tanıma modeli yükle
# with open("encodings.pickle", "rb") as f:
#     model_data = pickle.load(f)
# known_encodings = model_data["encodings"]
# known_names = model_data["names"]

# # 📁 Ses tanıma modeli yükle
# with open("voice_encodings.pickle", "rb") as vf:
#     voice_model = pickle.load(vf)
# voice_encodings = voice_model["encodings"]
# voice_names = voice_model["names"]

# # 🎙️ Ses tanıma fonksiyonu
# def recognize_speaker(audio_data, fs=44100):
#     try:
#         y = audio_data.flatten().astype(np.float32) / 32768.0
#         mfcc = librosa.feature.mfcc(y=y, sr=fs, n_mfcc=13)
#         feature_vector = np.mean(mfcc.T, axis=0)

#         distances = [np.linalg.norm(feature_vector - enc) for enc in voice_encodings]
#         min_distance = min(distances)
#         if min_distance < 25:  # eşik değeri deneysel
#             matched_index = distances.index(min_distance)
#             return voice_names[matched_index]
#     except Exception as e:
#         print("[SES TANIMA HATASI]", e)
#     return None

# # 🔊 Ses verisini al ve analiz et
# def get_volume_and_speaker(duration=0.4, fs=44100):
#     try:
#         recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
#         sd.wait()
#         volume = np.linalg.norm(recording) / len(recording)
#         speaker_name = recognize_speaker(recording, fs)
#         return volume, speaker_name
#     except Exception as e:
#         print("[SES HATASI]", e)
#         return 0.0, None

# # ⏱ Ayarlar
# volume_threshold = 0.02
# speaking_times = defaultdict(float)
# last_spoken = defaultdict(float)
# MAX_DURATION = 60
# start_time = time.time()

# # 📷 Kamera başlat
# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Kamera başlatılamadı.")
#     exit()

# print("🎥 Takip başlatıldı...")

# # 🔁 Takip döngüsü
# while True:
#     elapsed_time = time.time() - start_time
#     if elapsed_time > MAX_DURATION:
#         print("⏱ Maksimum süre doldu.")
#         break

#     success, frame = cap.read()
#     if not success:
#         print("⚠️ Kare okunamadı.")
#         time.sleep(0.2)
#         continue

#     rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     boxes = face_recognition.face_locations(rgb)
#     encodings = face_recognition.face_encodings(rgb, boxes)

#     current_time = time.time()

#     volume, speaker_predicted = get_volume_and_speaker()

#     for (top, right, bottom, left), encoding in zip(boxes, encodings):
#         matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
#         name = "Bilinmiyor"

#         if True in matches:
#             matched_idxs = [i for i, b in enumerate(matches) if b]
#             counts = {}
#             for i in matched_idxs:
#                 counts[known_names[i]] = counts.get(known_names[i], 0) + 1
#             name = max(counts, key=counts.get)

#         if name != "Bilinmiyor" and volume > volume_threshold:
#             if speaker_predicted == name:
#                 elapsed = current_time - last_spoken.get(name, current_time)
#                 if elapsed < 1.5:
#                     speaking_times[name] += elapsed
#                 last_spoken[name] = current_time
#                 print(f"[✔️] {name} konuştu (yüz+ses)")
#             else:
#                 print(f"[⚠️] {name} yüzü görüldü ama ses {speaker_predicted}")

# # 📁 Sonuçları JSON olarak kaydet
# results = {name: int(duration) for name, duration in speaking_times.items()}
# with open("results.json", "w", encoding="utf-8") as f:
#     json.dump(results, f, ensure_ascii=False, indent=2)

# cap.release()
# print("✅ Takip tamamlandı ve sonuçlar kaydedildi.")
