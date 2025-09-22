# ---- Base image -------------------------------------------------------------
    FROM python:3.11-slim

    # Environment (faster, cleaner installs; friendlier logs)
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1 \
        DEBIAN_FRONTEND=noninteractive
    
    # System deps for audio handling (ffmpeg for pydub) + git (optional)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 git \
     && rm -rf /var/lib/apt/lists/*
    
    # ---- App setup --------------------------------------------------------------
    WORKDIR /app
    
    # 1) Install Python deps first (better layer caching)
    COPY requirements.txt requirements-dev.txt ./
    RUN python -m pip install -U pip \
     && pip install -r requirements.txt
    
    # 2) Copy app code (only what the app needs to run)
    COPY app ./app
    COPY core ./core

    # ---- Runtime ----------------------------------------------------------------
    EXPOSE 8501
    ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
    
    # Run the Streamlit app
    CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    