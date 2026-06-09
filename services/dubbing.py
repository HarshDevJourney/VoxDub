import os
import uuid
import tempfile
import subprocess

from gtts import gTTS

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG_PATH = "ffmpeg"


SPEAKER_VOICES = {
    "SPEAKER_00": {"lang": "hi", "tld": "com"},
    "SPEAKER_01": {"lang": "hi", "tld": "co.in"},
    "SPEAKER_02": {"lang": "en", "tld": "co.uk"},
    "SPEAKER_03": {"lang": "en", "tld": "com.au"},
}
DEFAULT_VOICE = {"lang": "hi", "tld": "com"}


def _get_duration(path):
    """Use ffmpeg (not ffprobe) to read duration — imageio_ffmpeg only ships ffmpeg."""
    result = subprocess.run(
        [FFMPEG_PATH, "-i", path],
        capture_output=True, text=True,
    )
    # Duration is in stderr even on "error" exit — parse it
    for line in result.stderr.splitlines():
        if "Duration:" in line:
            time_str = line.strip().split("Duration:")[1].split(",")[0].strip()
            h, m, s = time_str.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Could not parse duration from: {path}")


def _change_speed(input_path, output_path, speed):
    filters = []
    while speed > 2.0:
        filters.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        filters.append("atempo=0.5")
        speed *= 2.0
    filters.append(f"atempo={round(speed, 6)}")
    subprocess.run(
        [FFMPEG_PATH, "-y", "-i", input_path, "-filter:a", ",".join(filters), output_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )


def _to_wav(input_path, output_path, sample_rate=22050):
    subprocess.run(
        [FFMPEG_PATH, "-y", "-i", input_path, "-ac", "1", "-ar", str(sample_rate), output_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )


def generate_tts(segments, output_path=None):
    if not segments:
        raise ValueError("No segments provided.")

    total_duration = max(seg["end"] for seg in segments) + 1.0
    sample_rate = 22050
    tmpdir = tempfile.mkdtemp()
    wav_clips = []  # (wav_path, delay_ms)

    for i, seg in enumerate(segments):
        text = seg.get("text", "").strip()
        if not text:
            continue

        speaker = seg.get("speaker", "SPEAKER_00")
        voice = SPEAKER_VOICES.get(speaker, DEFAULT_VOICE)
        start_ms = int(seg["start"] * 1000)
        target_dur = seg["end"] - seg["start"]

        raw_mp3  = os.path.join(tmpdir, f"{i}_raw.mp3")
        sped_mp3 = os.path.join(tmpdir, f"{i}_sped.mp3")
        clip_wav = os.path.join(tmpdir, f"{i}_clip.wav")

        # 1. Generate TTS
        gTTS(text=text, lang=voice["lang"], tld=voice["tld"]).save(raw_mp3)

        # 2. Measure duration using ffmpeg stderr output
        actual_dur = _get_duration(raw_mp3)

        # 3. Speed-adjust to fit the time slot
        if actual_dur > 0 and abs(actual_dur - target_dur) > 0.05:
            speed = actual_dur / target_dur
            _change_speed(raw_mp3, sped_mp3, speed)
            source = sped_mp3
        else:
            source = raw_mp3

        # 4. Convert to mono WAV — ffmpeg owns the file, no Python locks
        _to_wav(source, clip_wav, sample_rate=sample_rate)
        wav_clips.append((clip_wav, start_ms))

    if not wav_clips:
        raise ValueError("All segments were empty — nothing to mix.")

    # Silent base track
    silence_wav = os.path.join(tmpdir, "silence.wav")
    subprocess.run(
        [
            FFMPEG_PATH, "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r={sample_rate}:cl=mono",
            "-t", str(total_duration),
            silence_wav,
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )

    # Mix all clips in one filter_complex pass
    inputs = ["-i", silence_wav]
    for wav_path, _ in wav_clips:
        inputs += ["-i", wav_path]

    filter_parts = []
    mix_labels = ["[0]"]
    for idx, (_, delay_ms) in enumerate(wav_clips, start=1):
        label = f"[d{idx}]"
        filter_parts.append(f"[{idx}]adelay={delay_ms}|{delay_ms}{label}")
        mix_labels.append(label)

    mix_inputs = "".join(mix_labels)
    filter_parts.append(
        f"{mix_inputs}amix=inputs={len(mix_labels)}:duration=first:normalize=0[out]"
    )

    mixed_wav = os.path.join(tmpdir, "mixed.wav")
    result = subprocess.run(
        [
            FFMPEG_PATH, "-y",
            *inputs,
            "-filter_complex", ";".join(filter_parts),
            "-map", "[out]",
            mixed_wav,
        ],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg mix failed:\n{result.stderr.decode('utf-8', errors='replace')}"
        )

    # Export final MP3
    if output_path is None:
        os.makedirs("dubbed_output", exist_ok=True)
        output_path = os.path.join("dubbed_output", f"dubbed_{uuid.uuid4().hex[:8]}.mp3")

    subprocess.run(
        [FFMPEG_PATH, "-y", "-i", mixed_wav, "-q:a", "2", output_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
    )

    # Cleanup
    for f in os.listdir(tmpdir):
        try:
            os.remove(os.path.join(tmpdir, f))
        except Exception:
            pass
    try:
        os.rmdir(tmpdir)
    except Exception:
        pass

    return output_path