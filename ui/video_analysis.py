# ui/video_analysis.py

from controller.video.youtube_video_analysis import analyze_video
from tkinter import messagebox

def video_analysis():
    try:
        video_path = "data/videos/doga.mp4"  # Videonun yolu
        results = analyze_video(video_path)    # Liste olarak dönecek
        if results:
            messagebox.showinfo("Tanıma Sonuçları", "\n".join(results))
        else:
            messagebox.showwarning("Sonuç", "Hiçbir yüz tanınamadı.")
    except Exception as e:
        messagebox.showerror("Hata", f"Video analiz sırasında hata oluştu:\n{e}")
        
if __name__ == "__main__":
    video_analysis()