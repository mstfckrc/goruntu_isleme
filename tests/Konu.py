import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from controller.topics.get_topics import get_topics_from_keywords
from speech_recognition import Recognizer, AudioFile

def transcribe_audio_to_text(audio_file):
    recognizer = Recognizer()
    with AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data, language="tr") 
    return text

class TestTopicAnalysis(unittest.TestCase):

    def test_get_topics_from_audio(self):
        test_audio_file = "data/records/Doğa/Doğa_1.wav"  
        test_sentence = transcribe_audio_to_text(test_audio_file)
        
        print(f"Transcribed sentence: {test_sentence}")
        
        result = get_topics_from_keywords(test_sentence)

        expected_topic = "Çevre"  
        print(f"Detected topic: {result}")

        self.assertEqual(result, expected_topic, f"Beklenen konu '{expected_topic}', ancak '{result}' bulundu.")
        
if __name__ == "__main__":
    unittest.main()
