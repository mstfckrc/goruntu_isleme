from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from controller.video.youtube_downloader import download_with_ytdlp
from controller.video.fix_video import reencode_video
from controller.video.analyze_recorded_video import analyze_recorded_video

router = APIRouter()

class AnalyzeRequest(BaseModel):
    youtube_url: str
    filename: str

@router.post("/api/video/analyze")
def analyze_video(req: AnalyzeRequest):
    try:
        filename = req.filename if req.filename.endswith(".mp4") else req.filename + ".mp4"
        raw_path = download_with_ytdlp(req.youtube_url, filename)
        fixed_path = reencode_video(raw_path)

        if not os.path.exists(fixed_path):
            raise HTTPException(status_code=404, detail="Video işlenemedi veya bulunamadı.")

        results = analyze_recorded_video(fixed_path)
        return results or {}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))