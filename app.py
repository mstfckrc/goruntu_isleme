import tkinter as tk
from controller.audio.record_user import record_user_voice
from controller.emotion.record_user_emotion import record_user_emotion
from controller.face.face_controller import recognize_face
from globals import set_root as setRoot
from ui.story1 import user_story_1
from ui.story2 import user_story_2
from ui.story3 import user_story_3
from ui.video_analysis import video_analysis

def show_main_menu():
    """Ana menüyü gösterir."""
    for widget in root.winfo_children():
        widget.pack_forget()

    menu_label = tk.Label(root, text="Ana Menü", font=("Arial", 24))
    menu_label.pack(pady=20)

    tk.Button(root, text="Kullanıcı Sesi Kaydetme", command=record_user_voice, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Kullanıcı Duygu Kaydetme", command=record_user_emotion, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="User Story 1: Histogram", command=user_story_1, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="User Story 2: Ses Tanıma", command=user_story_2, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="User Story 3: Anlık Kişi Tanıma", command=user_story_3, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Yüz Tanıma", command=recognize_face, font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="Çıkış", command=root.quit, font=("Arial", 16)).pack(pady=20)
    tk.Button(root, text="🎥 Video Analizi", command=video_analysis, font=("Arial", 16)).pack(pady=10)
root = tk.Tk()
root.geometry("800x600")
setRoot(root)
root.title("Ses Analizi ve Tanıma")
show_main_menu()
root.mainloop()
