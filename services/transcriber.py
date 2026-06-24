import json
import os
from functools import lru_cache
from subprocess import CalledProcessError, run

import imageio_ffmpeg
import numpy as np
import soundfile as sf
import torch
import whisper
import whisper.audio as whisper_audio
from dotenv import load_dotenv
from pyannote.audio import Pipeline

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

_FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()


@lru_cache(maxsize=1)
def _patch_whisper_ffmpeg():
    """Whisper expects `ffmpeg` on PATH; imageio ships a differently named binary."""

    def load_audio(file: str, sr: int = whisper_audio.SAMPLE_RATE):
        cmd = [
            _FFMPEG,
            "-nostdin",
            "-threads",
            "0",
            "-i",
            file,
            "-f",
            "s16le",
            "-ac",
            "1",
            "-acodec",
            "pcm_s16le",
            "-ar",
            str(sr),
            "-",
        ]
        try:
            out = run(cmd, capture_output=True, check=True).stdout
        except CalledProcessError as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    whisper_audio.load_audio = load_audio


_patch_whisper_ffmpeg()


def get_speaker(start, end, diarization_segments):
    overlaps = {}

    for seg_start, seg_end, speaker in diarization_segments:
        overlap = min(end, seg_end) - max(start, seg_start)

        if overlap > 0:
            overlaps[speaker] = overlaps.get(speaker, 0) + overlap

    if not overlaps:
        return "UNKNOWN"

    return max(overlaps, key=overlaps.get)


def _run_diarization(audio_path: str):
    if not HF_TOKEN:
        return []

    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=HF_TOKEN,
        )

        waveform, sample_rate = sf.read(audio_path)
        waveform = torch.tensor(waveform, dtype=torch.float32)

        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        else:
            waveform = waveform.T

        output = pipeline({"waveform": waveform, "sample_rate": sample_rate})

        if hasattr(output, "speaker_diarization"):
            annotation = output.speaker_diarization
        else:
            annotation = output

        segments = []
        for turn, _, speaker in annotation.itertracks(yield_label=True):
            segments.append((turn.start, turn.end, speaker))

        return segments
    except Exception as exc:
        print(f"Diarization skipped: {exc}")
        return []


def transcribe(audio_path: str):
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = whisper.load_model("base")

    result = model.transcribe(audio_path, word_timestamps=True)
    whisper_segments = result["segments"]

    diarization_segments = _run_diarization(audio_path)

    transcript = []
    for seg in whisper_segments:
        speaker = (
            get_speaker(seg["start"], seg["end"], diarization_segments)
            if diarization_segments
            else "SPEAKER_00"
        )
        transcript.append(
            {
                "speaker": speaker,
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip(),
            }
        )

    output_folder = "transcribes"
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, "transcript.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=4, ensure_ascii=False)

    return transcript
