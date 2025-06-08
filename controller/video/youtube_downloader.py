import yt_dlp
from pathlib import Path

def download_with_ytdlp(link, filename="doga.mp4"):
    output_dir = Path("data/videos")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    ydl_opts = {
        'outtmpl': str(output_path),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

    print("🎬 Video başarıyla indirildi:", output_path)
    return str(output_path)
