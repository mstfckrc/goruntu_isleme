import subprocess
from pathlib import Path

def reencode_video(input_path, output_path=None):
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_stem(input_path.stem + "_fixed")

    output_path = output_path.with_suffix(".mp4")

    command = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        str(output_path)
    ]

    print(f"[FFMPEG] Videoyu yeniden kodluyor: {output_path.name}")
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return str(output_path)
