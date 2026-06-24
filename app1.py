import streamlit as st
import os
import time
import json
import time
from services.dubbing import generate_tts
from services.extract_audio_video import extract_content
from services.merge import merge_video
from services.transcriber import transcribe
from services.translator import translate

st.set_page_config(
    page_title="VoxDub — AI Video Dubbing",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e6e0;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0a0a0f;
}

.block-container {
    max-width: 780px !important;
    margin: auto !important;
    padding: 2rem 1.5rem 4rem !important;
}

[data-testid="stSidebar"] { display: none; }
[data-testid="stHeader"] { display: none; }
footer { display: none; }

/* ---------- HEADER ---------- */
.vd-header {
    text-align: center;
    padding: 2.5rem 0 2rem;
    border-bottom: 1px solid #1e1e28;
}
.vd-logo {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6e6b62;
    margin-bottom: 20px;
}
.vd-logo span {
    width: 6px; height: 6px;
    background: #c8a97e;
    border-radius: 50%;
    display: inline-block;
}
.vd-title {
    font-family: 'Syne', sans-serif;
    font-size: 52px;
    font-weight: 800;
    line-height: 1.05;
    color: #f0ece4;
    margin-bottom: 14px;
    letter-spacing: -0.02em;
}
.vd-title em {
    font-style: normal;
    color: #c8a97e;
}
.vd-sub {
    font-size: 15px;
    color: #6e6b62;
    font-weight: 300;
    letter-spacing: 0.01em;
}

/* ---------- UPLOAD BOX ---------- */
.upload-wrapper {
    border: 1px solid #1e1e28;
    border-radius: 20px;
    background: #0f0f17;
    padding: 0;
    margin-bottom: 24px;
    overflow: hidden;
    position: relative;
}
.upload-wrapper::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(200,169,126,0.06) 0%, transparent 65%);
    pointer-events: none;
}

[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 52px 40px !important;
    text-align: center !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    color: #6e6b62 !important;
    text-align: center !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: rgba(200,169,126,0.12) !important;
    color: #c8a97e !important;
    border: 1px solid rgba(200,169,126,0.3) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    padding: 8px 20px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: rgba(200,169,126,0.2) !important;
}

[data-testid="stFileUploaderDropzone"] svg {
    color: #c8a97e !important;
    width: 36px !important;
    height: 36px !important;
}

/* ---------- UPLOADED VIDEO ---------- */
.video-preview-wrap {
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 16px;
    border: 1px solid red;
}

[data-testid="stVideo"] {
    border-radius: 16px;
    overflow: hidden;
}

/* ---------- SUCCESS / INFO ---------- */
.success-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    color: #4ade80;
    border-radius: 100px;
    padding: 6px 16px;
    font-size: 13px;
    font-weight: 500;
    margin-bottom: 16px;
}

.path-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #141420;
    border: 1px solid #1e1e28;
    color: #6e6b62;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    font-family: 'DM Mono', monospace;
    margin-bottom: 20px;
}

/* ---------- LANGUAGE SELECTS ---------- */
.lang-section {
    margin-bottom: 24px;
}
.lang-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6e6b62;
    margin-bottom: 8px;
    display: block;
    font-family: 'Syne', sans-serif;
}

[data-testid="stSelectbox"] label {
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #6e6b62 !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    background: #0f0f17 !important;
    border: 1px solid #1e1e28 !important;
    border-radius: 12px !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
    border-color: rgba(200,169,126,0.4) !important;
}
[data-baseweb="popover"] {
    background: #12121a !important;
    border: 1px solid #1e1e28 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[role="option"] {
    background: transparent !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[role="option"]:hover, [aria-selected="true"] {
    background: rgba(200,169,126,0.1) !important;
    color: #c8a97e !important;
}

/* ---------- DIVIDER ---------- */
.arrow-divider {
    text-align: center;
    color: #c8a97e;
    font-size: 20px;
    padding: 0 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 28px;
}

/* ---------- BUTTON ---------- */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c8a97e 0%, #b8966a 100%) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 14px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;          /* was 5px */
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 14px 28px !important;
    height: auto !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:disabled {
    opacity: 0.7 !important;
    cursor: not-allowed !important;
}

/* shrink the × remove-file button */
[data-testid="stFileUploaderDeleteBtn"] button {
    width: 20px !important;
    height: 20px !important;
    min-width: unset !important;
    padding: 0 !important;
    border-radius: 50% !important;
    background: #1e1e28 !important;
    border: 1px solid #2e2e3a !important;
}
[data-testid="stFileUploaderDeleteBtn"] button svg {
    width: 10px !important;
    height: 10px !important;
    color: #6e6b62 !important;
}

/* ---------- PIPELINE ---------- */
.pipeline-wrap {
    background: #0f0f17;
    border: 1px solid #1e1e28;
    border-radius: 20px;
    overflow: hidden;
    margin-top: 24px;
}
.pipeline-header {
    padding: 16px 20px;
    border-bottom: 1px solid #1e1e28;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.pipeline-title {
    font-family: 'Syne', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6e6b62;
}
.job-id {
    font-size: 12px;
    color: #c8a97e;
    font-family: monospace;
    background: rgba(200,169,126,0.08);
    border: 1px solid rgba(200,169,126,0.2);
    padding: 3px 10px;
    border-radius: 6px;
}
.stage-row {
    padding: 14px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    border-bottom: 1px solid #1a1a22;
    transition: background 0.2s;
}
.stage-row:last-child { border-bottom: none; }
.stage-icon {
    width: 34px; height: 34px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
}
.stage-icon.done { background: rgba(34,197,94,0.1); color: #4ade80; }
.stage-icon.active { background: rgba(200,169,126,0.12); color: #c8a97e; }
.stage-icon.idle { background: #141420; color: #3a3a4a; }
.stage-text { flex: 1; }
.stage-name {
    font-size: 14px;
    font-weight: 500;
    color: #e8e6e0;
    margin-bottom: 2px;
}
.stage-desc { font-size: 12px; color: #6e6b62; }
.stage-done-icon { color: #4ade80; font-size: 13px; }

/* ---------- PROGRESS BAR ---------- */
.prog-outer {
    height: 3px;
    background: #1e1e28;
    border-radius: 2px;
    overflow: hidden;
    margin: 0 20px 20px;
}
.prog-inner {
    height: 100%;
    background: linear-gradient(90deg, #c8a97e, #e8c99e);
    border-radius: 2px;
    transition: width 0.3s ease;
}

/* ---------- RESULT ---------- */
.result-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 20px 0;
}
.result-card {
    background: #0f0f17;
    border: 1px solid #1e1e28;
    border-radius: 14px;
    padding: 16px;
}
.result-card .rc-label {
    font-size: 11px; color: #6e6b62;
    font-family: 'Syne', sans-serif;
    font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; margin-bottom: 6px;
}
.result-card .rc-val {
    font-size: 26px; font-weight: 700;
    color: #f0ece4; font-family: 'Syne', sans-serif;
}

.dl-btn {
    display: block;
    width: 100%;
    padding: 14px;
    background: #0f0f17;
    border: 1px solid rgba(200,169,126,0.3);
    border-radius: 14px;
    color: #c8a97e;
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 700;
    text-align: center;
    cursor: pointer;
    margin-top: 8px;
    letter-spacing: 0.05em;
}

/* ---------- STALE STREAMLIT ELEMENTS ---------- */
[data-testid="stMarkdownContainer"] p { color: #e8e6e0; }
.stAlert { border-radius: 12px !important; }
[data-testid="stSpinner"] { color: #c8a97e !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="vd-header">
  <div class="vd-logo"><span></span> VoxDub Studio <span></span></div>
  <div class="vd-title">Dub videos with<br><em>AI voices</em></div>
</div>
""", unsafe_allow_html=True)

# ── Upload ───────────────────────────────────────────────────────────────
st.markdown("<div class='upload-wrapper'>", unsafe_allow_html=True)
video_file = st.file_uploader(
    "upload",
    type=["mp4", "mov", "avi", "mkv"],
    label_visibility="collapsed"
)
st.markdown("</div>", unsafe_allow_html=True)

# ── Uploaded preview ─────────────────────────────────────────────────────
video_path = None
if video_file:
    os.makedirs("uploads", exist_ok=True)
    video_path = os.path.join("uploads", video_file.name)
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    st.markdown(
        f"<div class='success-pill'>✓ Uploaded — {video_file.name}</div>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='video-preview-wrap'>", unsafe_allow_html=True)
    st.video(video_path)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='path-tag'>📁 uploads/{video_file.name}</div>",
        unsafe_allow_html=True
    )

# ── Language selectors ────────────────────────────────────────────────────
LANGS = ["English", "Hindi", "Spanish", "French", "German", "Japanese", "Portuguese", "Arabic"]

col1, arrow_col, col2 = st.columns([5, 1, 5])

with col1:
    source_lang = st.selectbox("Source language", LANGS, index=0)

with arrow_col:
    st.markdown("<div class='arrow-divider'>→</div>", unsafe_allow_html=True)

with col2:
    target_lang = st.selectbox("Target language", LANGS, index=1)

st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)


# ── Pipeline ──────────────────────────────────────────────────────────────
STAGES = [
    ("🎵", "Extract audio",       "FFmpeg strips audio from video"),
    ("📝", "Transcription",       "Whisper converts speech to text"),
    ("🌍", "Translation",         f"Argos Translate → {target_lang if 'target_lang' in dir() else 'target'}"),
    ("🎙️", "Voice synthesis",     "Coqui TTS generates dubbed audio"),
    ("🎬", "Assemble video",      "FFmpeg merges audio + video"),
]

            
                
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

btn_label = "⏳ Dubbing in progress..." if st.session_state.is_processing else "⚡ Start Dubbing"
process = st.button(btn_label, use_container_width=True, disabled=st.session_state.is_processing)


if process:
    if not video_file:
        st.error("Please upload a video first.")
    else:
        st.session_state.is_processing = True
        st.rerun()


if st.session_state.is_processing and video_file:
    progress_bar = st.progress(0)
    status = st.empty()

    try:
        # Step 1
        status.info("🎵 Extracting audio...")
        # audio_path, video_only_path = extract_content(video_path)
        progress_bar.progress(20)
        time.sleep(10)
        # Step 2
        status.info("📝 Transcribing speech...")
        # transcript = transcribe(audio_path)
        progress_bar.progress(50)
        
        time.sleep(10)

        # Step 3
        status.info(f"🌍 Translating to {target_lang}...")
        # translated = translate(transcript, source_lang, target_lang)
        progress_bar.progress(70)
        
        time.sleep(10)

        # Step 4
        status.info("🎙️ Generating dubbed voices...")
        # dubbed_audio = generate_tts(translated)
        progress_bar.progress(90)
        
        time.sleep(10)

        # Step 5
        status.info("🎬 Merging audio and video...")
        # final_video = merge_video(video_path=video_only_path, audio_path=dubbed_audio)
        progress_bar.progress(100)
        

        final_video = "merged_output\merged_9ab8aebf.mp4"  # Placeholder for the final video path

        status.success("✅ Dubbing complete!")
        st.success(f"Generated: {final_video}")

        if os.path.exists(final_video):
            st.video(final_video)
            with open(final_video, "rb") as f:
                st.download_button(
                    "⬇ Download Dubbed Video",
                    data=f,
                    file_name=os.path.basename(final_video),
                    mime="video/mp4"
                )
    except Exception as e:
        status.error(f"❌ Error: {e}")
    finally:
        st.session_state.is_processing = False
