<div align="center">

![VoxDub Banner](https://github.com/user-attachments/assets/2554e11f-6ca6-4865-85cf-7f1803f706b3)

# VoxDub — AI Video Dubbing

**Automatically dub any video into another language using AI.**
Upload → Transcribe → Translate → Synthesize → Download.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-imageio-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

</div>

---

## Project Resources

| Asset | Platform | URL |
|-------|----------|-----|
| |
| Demonstration Demo | Google Drive | [View Demo](https://drive.google.com/drive/folders/1Ph3_UswBHMHVEarztDvkCe9q_sEGWn8a) |

---

## What it does

VoxDub is an end-to-end AI video dubbing system that automates the translation and revoicing of spoken content while maintaining timing synchronization. The system ingests source video assets, decouples the underlying audio stream, recognizes and timestamps multi-speaker dialogue, translates text segments into a target language, synthesizes matching vocal assets, and merges the new audio tracks back into the original video container — all orchestrated inside an intuitive web interface.

---

## Technology Stack

| Layer | Core Module | Functional Responsibility |
|-------|-------------|--------------------------|
| Backend Runtime | Python 3.10+ | Coordinates sequential lifecycle logic and orchestration pipelines |
| User Interface | Streamlit | Serves interactive input controls, localized video players, and state handling |
| Speech Engine | OpenAI Whisper | Provides automated speech recognition (ASR) alongside precise text timestamps |
| Diarization | PyAnnote.audio | Evaluates voice signatures to classify distinct speaker turns and identities |
| Translation | deep_translator | Bridges content blocks across structural target language definitions |
| Voice Synthesis | gTTS | Outputs synthetic localized voice waveforms based on structured string payloads |
| Media Processing | FFmpeg | Directs audio extraction, bit-rate formatting, timeline syncing, and final muxing |

---

## Processing Pipeline

```
source_video.mp4
      │
      ├─ 1. Video Upload ──────────────► Streamlit UI Hub
      │
      ├─ 2. Audio Extraction ──────────► FFmpeg → raw_audio.wav + video_only.mp4
      │
      ├─ 3. Transcription ─────────────► OpenAI Whisper → text segments
      │
      ├─ 4. Diarization ───────────────► PyAnnote.audio → diarized_metadata.json
      │
      ├─ 5. Translation ───────────────► deep_translator → translated_payload.json
      │
      ├─ 6. Voice Synthesis ───────────► gTTS Audio Engine → dubbed_voice.mp3
      │   (per-speaker voices,
      │    speed-fitted to slots)
      │
      ├─ 7. Timing Alignment ──────────► Timestamp Sync → synced_audio.wav
      │
      └─ 8. Mux Video Output ──────────► FFmpeg Merge → final_dubbed.mp4
```

Speaker voices are assigned from a map — each `SPEAKER_XX` gets a distinct gTTS language/accent so voices are distinguishable in the output.

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/HarshDevJourney/VoxDub.git
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

Get your free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). It is used for speaker diarization (identifying who is speaking).

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

## Supported languages

Any language pair supported by Google Translate. TTS output quality is best for:

`Hindi · English · Spanish · French · German · Portuguese · Japanese · Arabic`

---

<div align="center">
Built with Streamlit · Whisper · PyAnnote · gTTS · FFmpeg
</div>