import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
import numpy as np
import librosa
from model.audio.speakers_data import load_speakers_data
from model.audio.train_speaker import train_speaker_model 
from globals import get_audio_accuracy as getAudioAccuracy, get_audio_f1_score as getAudioF1Score

class TestSpeakerRecognitionModel(unittest.TestCase):

    def load_audio_data(audio_file, sample_rate=22050):
        """Verilen ses dosyasını yükler ve ses verisini döndürür."""
        audio_data, sr = librosa.load(audio_file, sr=sample_rate)
        return audio_data, sr

class TestSpeakerRecognitionModel(unittest.TestCase):

    def test_train_speaker_model(self):
        """Konuşmacı tanıma modelinin doğru çalıştığını test et."""
        print("test_train_speaker_model çalıştı.")
        result = train_speaker_model()
        self.assertTrue(result, "Konuşmacı tanıma modeli eğitilemedi!")
        
        accuracy = getAudioAccuracy() 
        f1_score = getAudioF1Score()  
        
        print(f"Model Doğruluğu: {accuracy:.2f}")
        print(f"F1 Skoru: {f1_score:.2f}")
        
        self.assertGreater(accuracy, 0.7, f"Model doğruluğu beklenen değerin altında: {accuracy}")
        self.assertGreater(f1_score, 0.7, f"F1 skoru beklenen değerin altında: {f1_score}")

    def test_feature_extraction(self):
        """Özellik çıkarımının doğru yapılıp yapılmadığını test et."""
        print("test_feature_extraction çalıştı.")
        
        sample_audio_file = "data/records/Doğa/Doğa_1.wav"  
        
        audio_data, sample_rate = self.load_audio_data(sample_audio_file) 
        
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=20)
        self.assertEqual(mfccs.shape[0], 20, "MFCC sayısı yanlış!")
        self.assertGreater(np.mean(mfccs), 0, "MFCC değerleri beklenen aralıkta değil!")

if __name__ == "__main__":
    unittest.main()
