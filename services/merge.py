import os
import uuid
import subprocess
import imageio_ffmpeg

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def merge_video(video_path, audio_path):
    """
    Merge a video with dubbed audio.

    Args:
        video_path (str): Path to input video.
        audio_path (str): Path to dubbed audio.

    Returns:
        str: Path to merged output video.
    """

    os.makedirs("merged_output", exist_ok=True)

    output_path = os.path.join(
        "merged_output",
        f"merged_{uuid.uuid4().hex[:8]}.mp4"
    )

    cmd = [
        FFMPEG_PATH,
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path,
    ]

    try:
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise

    return output_path