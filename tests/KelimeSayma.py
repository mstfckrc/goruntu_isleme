import unittest
from speech_recognition import Recognizer, AudioFile

class TestSpeechToText(unittest.TestCase):
    def test_word_count(self):
        recognizer = Recognizer()
        audio_path = "data/records/Doğa/Doğa_1.wav"  
        
        with AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            try:
                
                text = recognizer.recognize_google(audio, language='tr')
                print("Metin:", text)  
        
                
                word_count = len(text.split())
                print("Kelime Sayısı:", word_count) 

                
                expected_word_count = 9
                self.assertEqual(word_count, expected_word_count)
            except Exception as e:
                print(f"Hata: {e}")
                self.fail(f"Ses dosyasından metin çıkarılamadı. {e}")

if __name__ == "__main__":
    unittest.main()
