![CI](https://github.com/aditeyaarya/tfds_project/actions/workflows/ci.yml/badge.svg)
**Docker Link:** https://hub.docker.com/r/aditeyaarya/diarization-app
# 🏛️ Transcription and Diarization Tool

This project is a **Streamlit web application** for analyzing audio/video files with:

- **Automatic Speech Recognition (ASR)** using [WhisperX](https://github.com/m-bain/whisperX)  
- **Speaker Diarization** using [pyannote.audio](https://github.com/pyannote/pyannote-audio)  

The project is containerized with Docker, tested with Pytest, styled with a custom Oxford–Cream–Bronze theme, and set up for CI in GitHub Actions.

---

## Features

- Upload audio/video files (`.mp3`, `.wav`, `.m4a`, `.flac`, `.mp4`, `.mov`)  
- Select Whisper model size (`tiny`, `base`, `small`, `medium`, `large-v2`, `large-v3`)  
- Choose device (`cpu`, `cuda`, `mps`)  
- Run transcription + diarization with a Hugging Face token (required for PyAnnote)  
- Preview transcripts with timestamps and speaker labels  
- Download results as **JSON**, **CSV**, or **TXT**  
- Optionally save outputs to your Desktop  
- Modern UI with Oxford green sidebar, cream background, and bronze buttons  

---

## ⚙️ Setup
Create a virtual environment and install dependencies:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**Run the app:**
streamlit run app/app.py


```bash
git clone https://github.com/aditeyaarya/tfds_project.git
cd tfds_project
