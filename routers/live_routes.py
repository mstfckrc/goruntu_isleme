from fastapi import APIRouter
from services.tracker_controller import start_tracker, stop_tracker, is_tracker_running
import json
import os

router = APIRouter(prefix="/api/live")

@router.post("/start")
def start():
    if start_tracker():
        return {"status": "started"}
    return {"status": "already_running"}

@router.post("/stop")
def stop():
    if stop_tracker():
        return {"status": "stopped"}
    return {"status": "not_running"}

@router.get("/status")
def status():
    return {"running": is_tracker_running()}

@router.get("/results")
def results():
    if os.path.exists("results.json"):
        with open("results.json", "r") as f:
            return json.load(f)
    return {}