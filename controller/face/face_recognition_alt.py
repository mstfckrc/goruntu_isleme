import os
import cv2
import face_recognition
import pickle

class FaceRecognitionAlt:
    def __init__(self, dataset_dir="data/faces", model_path="encodings.pickle"):
        self.dataset_dir = dataset_dir
        self.model_path = model_path
        self.known_encodings = []
        self.known_names = []

    def train(self):
        print("[EĞİTİM] Dataset taranıyor...")
        for person_name in os.listdir(self.dataset_dir):
            person_path = os.path.join(self.dataset_dir, person_name)
            if not os.path.isdir(person_path):
                continue
            for img_name in os.listdir(person_path):
                img_path = os.path.join(person_path, img_name)
                image = cv2.imread(img_path)
                if image is None:
                    continue
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(rgb, model="hog")
                encodings = face_recognition.face_encodings(rgb, boxes)
                for encoding in encodings:
                    self.known_encodings.append(encoding)
                    self.known_names.append(person_name)

        print(f"[EĞİTİM] {len(self.known_names)} yüz örneği işlendi.")
        self.save_model()


    def predict(self, frame):
        """
        Bir kare (frame) içindeki yüzleri tanır.
        Dönüş: (boxes, names)
        """
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)

        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.5)
            name = "Unknown"
            if True in matches:
                matched_idxs = [i for i, b in enumerate(matches) if b]
                counts = {}
                for i in matched_idxs:
                    counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1
                name = max(counts, key=counts.get)
            names.append(name)

        return boxes, names

    def save_model(self):
        with open(self.model_path, "wb") as f:
            pickle.dump({"encodings": self.known_encodings, "names": self.known_names}, f)
        print(f"[KAYIT] Model pickle dosyasına yazıldı: {self.model_path}")

    def load_model(self):
        with open(self.model_path, "rb") as f:
            data = pickle.load(f)
            self.known_encodings = data["encodings"]
            self.known_names = data["names"]
        print(f"[YÜKLEME] Model yüklendi. {len(self.known_names)} kişi.")

    def recognize_from_camera(self):
        self.load_model()
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, boxes)

            for (top, right, bottom, left), encoding in zip(boxes, encodings):
                matches = face_recognition.compare_faces(self.known_encodings, encoding, tolerance=0.5)
                name = "Bilinmiyor"
                if True in matches:
                    matched_idxs = [i for i, b in enumerate(matches) if b]
                    counts = {}
                    for i in matched_idxs:
                        counts[self.known_names[i]] = counts.get(self.known_names[i], 0) + 1
                    name = max(counts, key=counts.get)

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

            cv2.imshow("Yüz Tanıma (Alt)", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    fr = FaceRecognitionAlt(dataset_dir="data/faces", model_path="encodings.pickle")
    fr.train() 