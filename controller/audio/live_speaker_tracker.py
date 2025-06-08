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
        self.volume_threshold = 0.01
        self.max_duration = 20

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

    def start_tracking(self):
        self.start_time = time.time()
        self.last_speaker_time = time.time()
        self.load_model()
        self.load_voice_model()
        cap = cv2.VideoCapture(0)

        while True:
            elapsed_total = time.time() - self.start_time
            if elapsed_total > self.max_duration:
                print("\n⏱ Maksimum izleme süresi doldu (20 saniye). Çıkılıyor...")
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
                if voice_name:
                    print(f"[ALGILANAN] {voice_name} konuşuyor olabilir.")
                    if voice_name in detected_names:
                        now = time.time()
                        elapsed = now - self.last_speaker_time
                        self.speaking_times[voice_name] += elapsed
                        self.last_speaker_time = now
                        self.current_speaker = voice_name

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
