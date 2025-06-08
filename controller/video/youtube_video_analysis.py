import cv2
from controller.face.face_recognition_service import FaceRecognitionService

def analyze_video(video_path):
    svc = FaceRecognitionService()
    if not svc.train_model():
        print("Model eğitilemedi.")
        return []

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    counts = {}

    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        print(f"[KARE] {len(faces)} yüz bulundu")

        for (x, y, w, h) in faces:
            face_img = gray[y:y+h, x:x+w]
            resized = cv2.resize(face_img, (100, 100))
            _, buf = cv2.imencode('.jpg', resized)
            label = svc.recognize(buf.tobytes())
            if label:
                counts[label] = counts.get(label, 0) + 1

    cap.release()

    results = [f"{person}: {count / fps:.1f} saniye" for person, count in counts.items()]
    return results
