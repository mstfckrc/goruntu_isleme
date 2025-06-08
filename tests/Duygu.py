import os
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import librosa
import numpy as np
from model.emotion.emotion_train_speaker import train_emotion_model

def test_emotion_model(model, label_encoder, scaler, test_files):
    """Eğitilen modeli test etmek için kullanılır."""
    X_test = []
    for file in test_files:
        audio, sr = librosa.load(file, sr=None)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        mfccs_mean = np.mean(mfccs.T, axis=0)
        X_test.append(mfccs_mean)

    X_test = np.array(X_test)
    X_test = scaler.transform(X_test)

    predictions = model.predict(X_test)
    predicted_emotions = label_encoder.inverse_transform(predictions)

    for file, emotion in zip(test_files, predicted_emotions):
        print(f"Dosya: {file} -> Tahmin edilen duygu: {emotion}")


test_files = [
    "data/records/Ceyda/Ceyda_3.wav",
    "data/records/Ceyda/Ceyda_2.wav",  
    "data/records/Ceyda/Ceyda_1.wav"  
]

model,label_encoder,scaler=train_emotion_model()
test_emotion_model(model,label_encoder,scaler, test_files)
