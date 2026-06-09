import json
import os
import tempfile
import subprocess
import numpy as np
import imageio_ffmpeg
import torch

import torchaudio
import whisper.audio as whisper_audio
import whisper

import soundfile as sf
from pyannote.audio import Pipeline

from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError(
        "HF_TOKEN environment variable not found."
    )



def get_speaker(start, end, diarization_segments):
    overlaps = {}

    for seg_start, seg_end, speaker in diarization_segments:
        overlap = min(end, seg_end) - max(start, seg_start)

        if overlap > 0:
            overlaps[speaker] = (
                overlaps.get(speaker, 0) + overlap
            )

    if not overlaps:
        return "UNKNOWN"

    return max(overlaps, key=overlaps.get)



def transcribe(audio_path: str):

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Audio file not found: {audio_path}"
        )

    model = whisper.load_model("base")

    result = model.transcribe(
        audio_path,
        word_timestamps=True
    )

    whisper_segments = result["segments"]

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        token=HF_TOKEN
    )

    waveform, sample_rate = sf.read(audio_path)

    waveform = torch.tensor(waveform, dtype=torch.float32)

    # Convert to (channels, samples)
    if waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)
    else:
        waveform = waveform.T
    
    output = pipeline({
        "waveform": waveform,
        "sample_rate": sample_rate
    })
    
    annotation = output.speaker_diarization
    
    print(annotation)

    diarization_segments = []
    transcript = []

    for turn, _, speaker in annotation.itertracks(yield_label=True):
        segment = (
            turn.start,
            turn.end,
            speaker
        )
        diarization_segments.append(segment)

    for seg in whisper_segments:
        transcript.append(
            {
                "speaker": get_speaker(
                    seg["start"],
                    seg["end"],
                    diarization_segments
                ),
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip()
            }
        )

    output_folder = "transcribes"
    os.makedirs(output_folder, exist_ok=True)

    output_file = os.path.join(output_folder, "transcript.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=4, ensure_ascii=False)

    return transcript