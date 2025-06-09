import os
import pickle
import numpy as np
import librosa

DATA_DIR = "data/records"
VOICE_MODEL_PATH = "voice_encodings.pickle"

def extract_features(file_path):
    y, sr = librosa.load(file_path, sr=16000)  # ✅ sabit sample rate
    y = librosa.util.normalize(y)              # ✅ normalize
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    return np.mean(mfcc.T, axis=0)             # ✅ ortalama vektör

def train_voice_models():
    encodings = []
    names = []

    for person_name in os.listdir(DATA_DIR):
        person_path = os.path.join(DATA_DIR, person_name)
        if not os.path.isdir(person_path):
            continue

        for file_name in os.listdir(person_path):
            if not file_name.endswith(".wav"):
                continue

            file_path = os.path.join(person_path, file_name)
            try:
                features = extract_features(file_path)
                encodings.append(features)
                names.append(person_name)
                print(f"[OK] {file_name} -> {person_name}")
            except Exception as e:
                print(f"[HATA] {file_name}: {e}")

    with open(VOICE_MODEL_PATH, "wb") as f:
        pickle.dump({"encodings": encodings, "names": names}, f)

    print(f"\nToplam {len(encodings)} ses kaydı işlendi.")



if __name__ == "__main__":
    train_voice_models()