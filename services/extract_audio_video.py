import os
import subprocess
import logging
from pathlib import Path
import imageio_ffmpeg

logger = logging.getLogger(__name__)

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

class AudioExtractionError(Exception):
    pass


def extract_content(video_path: str) -> tuple[str, str]:
    video_path = str(Path(video_path).resolve())

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    base = os.path.splitext(video_path)[0]
    audio_path = f"{base}_audio.wav"
    video_only_path = f"{base}_video_only.mp4"

    # Extract Audio
    _run_ffmpeg(
        [
            FFMPEG_PATH,
            "-y",
            "-i",
            video_path,
            "-vn",
            "-af", "volume=5.0",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path,
        ],
        f"Failed to extract audio from {video_path}",
    )

    # Extract Video Only
    _run_ffmpeg(
        [
            FFMPEG_PATH,
            "-y",
            "-i",
            video_path,
            "-an",
            "-c:v",
            "copy",
            video_only_path,
        ],
        f"Failed to create video-only file from {video_path}",
    )

    _assert_output(audio_path, "Audio")
    _assert_output(video_only_path, "Video-only")

    logger.info(
        "Extracted audio → %s (%.1f MB)",
        audio_path,
        _mb(audio_path),
    )

    logger.info(
        "Extracted video → %s (%.1f MB)",
        video_only_path,
        _mb(video_only_path),
    )

    return audio_path, video_only_path


def _run_ffmpeg(args: list[str], error_msg: str) -> None:
    try:
        result = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except Exception as e:
        raise AudioExtractionError(
            f"Failed to execute FFmpeg.\n{str(e)}"
        )

    if result.returncode != 0:
        raise AudioExtractionError(
            f"{error_msg}\n"
            f"FFmpeg exit code: {result.returncode}\n\n"
            f"{result.stderr}"
        )


def _assert_output(path: str, label: str) -> None:
    if not os.path.exists(path):
        raise AudioExtractionError(
            f"{label} output file was not created: {path}"
        )

    if os.path.getsize(path) == 0:
        raise AudioExtractionError(
            f"{label} output file is empty: {path}"
        )


def _mb(path: str) -> float:
    return os.path.getsize(path) / (1024 * 1024)