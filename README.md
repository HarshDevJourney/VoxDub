<div align="center">

<img src="<img width="878" height="312" alt="image" src="https://github.com/user-attachments/assets/2554e11f-6ca6-4865-85cf-7f1803f706b3" />
" />

# VoxDub — AI Video Dubbing

**Automatically dub any video into another language using AI.**  
Upload → Transcribe → Translate → Synthesize → Download.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-imageio-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## What it does

VoxDub takes any video file, strips the audio, transcribes the speech with Whisper, translates it, generates new voiced audio with speaker-aware TTS, and merges it back into the original video — all from a single Streamlit UI.

| Step | Tool |
|------|------|
| Extract audio | FFmpeg via `imageio-ffmpeg` |
| Transcribe speech | OpenAI Whisper |
| Translate text | `deep_translator` (Google Translate) |
| Generate dubbed audio | gTTS (speaker-aware voices) |
| Merge back into video | FFmpeg (copy stream + AAC fallback) |

---

## Screenshots

> Upload a video, pick languages, hit Start Dubbing — get a downloadable dubbed MP4.

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/voxdub.git
cd voxdub
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```env
HF_TOKEN=your_huggingface_token_here
```

Get your free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). It's used for speaker diarization (identifying who is speaking).

### 5. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501).

---

## Project structure

```
voxdub/
├── app.py                        # Streamlit UI + pipeline orchestrator
├── .env                          # HF_TOKEN (not committed)
├── requirements.txt
│
├── services/
│   ├── extract_audio_video.py    # FFmpeg: split video into audio + silent video
│   ├── transcriber.py            # Whisper: speech → diarized JSON segments
│   ├── translator.py             # deep_translator: translate segments
│   ├── dubbing.py                # gTTS + FFmpeg: generate speaker-aware dubbed audio
│   └── merge.py                  # FFmpeg: merge dubbed audio back into video
│
├── uploads/                      # Uploaded videos (auto-created)
├── transcribes/                  # Raw Whisper transcripts (JSON)
├── translated_output/            # Translated transcripts (JSON)
├── dubbed_output/                # Generated dubbed audio (MP3)
└── merged_output/                # Final dubbed videos (MP4)
```

---

## How the pipeline works

```
video.mp4
    │
    ├─ FFmpeg ──────────────────► audio.wav  +  video_only.mp4
    │
    ├─ Whisper + PyAnnote ──────► [{ speaker, start, end, text }, ...]
    │
    ├─ deep_translator ─────────► [{ speaker, start, end, text (translated) }, ...]
    │
    ├─ gTTS + FFmpeg ───────────► dubbed.mp3
    │   (per-speaker voices,         (clips overlaid at correct timestamps)
    │    speed-fitted to slots)
    │
    └─ FFmpeg merge ────────────► final_dubbed.mp4
```

Speaker voices are assigned from a map — each `SPEAKER_XX` gets a distinct gTTS language/accent so voices are distinguishable in the output.

---

## Requirements

```txt
streamlit
openai-whisper
deep-translator
gTTS
imageio-ffmpeg
pyannote.audio
python-dotenv
torch
```

FFmpeg is bundled via `imageio-ffmpeg` — no system install needed on Windows or macOS.

---

## Troubleshooting

**Merge fails with exit code 4294967294**  
This is a Windows FFmpeg crash on `-c:v copy` with variable frame rate recordings. The merge service automatically retries with `libx264` re-encoding as a fallback.

**`FileNotFoundError` in dubbing**  
Make sure you're using the latest `services/dubbing.py` — earlier versions used `pydub` which causes Windows file-lock issues. The current version uses pure FFmpeg with no pydub dependency.

**HF_TOKEN errors**  
Ensure your `.env` file exists in the project root and contains a valid `HF_TOKEN`. The token needs read access on Hugging Face.

**Slow processing**  
Whisper transcription and TTS generation are CPU-bound. A 2-minute video typically takes 3–6 minutes on CPU. GPU acceleration is supported automatically if CUDA is available.

---

## Supported languages

Any language pair supported by Google Translate. TTS output quality is best for:
`Hindi · English · Spanish · French · German · Portuguese · Japanese · Arabic`

---

## License

MIT — free to use, modify, and distribute. Add attribution if you build something cool with it.

---

<div align="center">
Built with Streamlit · Whisper · gTTS · FFmpeg
</div>
