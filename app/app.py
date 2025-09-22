import io
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st
import torch

# --- make project root importable (so core.* works) ---
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from core.io_utils import save_tmp, save_three_outputs_locally, as_segments  # noqa: E402
from core.turns import merge_words_to_turns, turns_to_txt, unique_speaker_count  # noqa: E402
from core.pipeline import run_pipeline  # noqa: E402


# ---- CSS loader ----
def load_css(filename: str = "app/ui_theme.css") -> str:
    css_path = Path(__file__).resolve().parent / filename
    try:
        return f"<style>{css_path.read_text(encoding='utf-8')}</style>"
    except FileNotFoundError:
        st.warning(f"Theme file not found: {css_path}")
        return ""


# ---- Page config ----
st.set_page_config(
    page_title="Transcription and Diarization Tool",
    page_icon="🏛️",
    layout="centered",
)

# inject css
BOARDROOM_CSS = load_css("ui_theme.css")
if BOARDROOM_CSS:
    st.markdown(BOARDROOM_CSS, unsafe_allow_html=True)


# ---- Title ----
st.title("🏛️ Transcription and Diarization Tool")


# ---- Sidebar controls ----
def _device_options() -> List[str]:
    opts = ["cuda", "cpu"]
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        opts.append("mps")
    return opts


with st.sidebar:
    st.header("Transcription Settings")

    MODEL_SIZE = st.selectbox(
        "Whisper model",
        ["tiny", "base", "small", "medium", "large-v2", "large-v3"],
        index=2,
    )

    LANGUAGE = st.text_input("Language (blank = auto)", value="")

    DEVICE_OPTS = _device_options()
    DEVICE_DEFAULT_INDEX = (
        0
        if torch.cuda.is_available()
        else (DEVICE_OPTS.index("mps") if "mps" in DEVICE_OPTS else DEVICE_OPTS.index("cpu"))
    )

    DEVICE = st.selectbox("Device (ASR/Align)", DEVICE_OPTS, index=DEVICE_DEFAULT_INDEX)

    HF_TOKEN = st.text_input("Hugging Face token (required)", value="", type="password")

    DIAR_DEVICE = st.selectbox("Diarization device", ["cpu", "cuda", "mps"], index=0)

    SAVE_LOCAL = st.checkbox("Also save to Desktop/<audio>_transcription", value=False)

uploaded = st.file_uploader(
    "Upload audio/video", type=["mp3", "wav", "m4a", "flac", "mp4", "mov"]
)


# ---- Main action ----
if st.button("Run"):
    if not uploaded:
        st.error("No file uploaded.")
        st.stop()

    HF_TOKEN = HF_TOKEN.strip()
    if not HF_TOKEN:
        st.error("Hugging Face token is required for diarization.")
        st.stop()

    # prepare paths
    input_path = save_tmp(uploaded)
    audio_name = Path(uploaded.name).stem
    out_dir = Path.home() / "Desktop" / f"{audio_name}_transcription"

    st.info("Running pipeline… (this may take time)")
    try:
        words, turns = run_pipeline(
            input_path=input_path,
            model_size=MODEL_SIZE,
            device=DEVICE,
            language=(LANGUAGE or None),
            hf_token=HF_TOKEN,
            diar_device=DIAR_DEVICE,
        )
    except Exception as e:
        st.error(f"❌ Pipeline failed: {e}")
        st.stop()

    # ---- Preview ----
    st.subheader("Preview")

    def _line(t: Dict[str, Any]) -> str:
        s = f"{int(t['start'] // 60):02d}:{t['start'] % 60:05.2f}"
        e = f"{int(t['end'] // 60):02d}:{t['end'] % 60:05.2f}"
        return f"[{s}-{e}] {t['speaker']}: {t.get('text', '')}"

    st.text_area(
        "Text",
        value="\n".join(_line(t) for t in turns[:150]),
        height=300,
        disabled=True,
    )

    # ---- Downloads ----
    json_words_bytes = json.dumps(words, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        f"⬇️ {audio_name}_words.json",
        data=json_words_bytes,
        file_name=f"{audio_name}_words.json",
        mime="application/json",
    )

    csv_buf = io.StringIO()
    writer = csv.DictWriter(csv_buf, fieldnames=["speaker", "start", "end", "text"])
    writer.writeheader()
    for t in turns:
        writer.writerow(
            {
                "speaker": t["speaker"],
                "start": t["start"],
                "end": t["end"],
                "text": (t.get("text") or "").replace("\n", " "),
            }
        )
    st.download_button(
        f"⬇️ {audio_name}_turns.csv",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name=f"{audio_name}_turns.csv",
        mime="text/csv",
    )

    txt_str = turns_to_txt(turns)
    st.download_button(
        f"⬇️ {audio_name}.txt",
        data=txt_str.encode("utf-8"),
        file_name=f"{audio_name}.txt",
        mime="text/plain",
    )

    # ---- Save locally if requested ----
    if SAVE_LOCAL:
        save_three_outputs_locally(
            out_dir,
            json_words_bytes,
            csv_buf.getvalue().encode("utf-8"),
            txt_str,
        )
        st.success(f"Saved to: {out_dir}")
