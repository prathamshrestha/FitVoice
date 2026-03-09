FROM mambaorg/micromamba:1.5.8

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 build-essential cmake git libgl1 ca-certificates \
    portaudio19-dev libasound2-dev \
    espeak-ng espeak-ng-data libespeak-ng1 \
 && rm -rf /var/lib/apt/lists/*

# create env
COPY environment.yml /tmp/environment.yml
RUN micromamba create -y -n voicebot -f /tmp/environment.yml && micromamba clean --all --yes

# expose env so we don't need micromamba at runtime
ENV PATH=/opt/conda/envs/voicebot/bin:$PATH \
    HOME=/home/mambauser \
    XDG_CACHE_HOME=/home/mambauser/.cache \
    HF_HOME=/home/mambauser/.cache/huggingface \
    COQUI_TTS_CACHE_DIR=/home/mambauser/.local/share/tts \
    PORT=8080

# (optional) pre-cache models at build time
ARG WHISPER_MODEL=tiny
ARG COQUI_TTS_MODEL=tts_models/en/ljspeech/vits
RUN micromamba run -n voicebot python -c "import os, whisper; whisper.load_model(os.getenv('WHISPER_MODEL','tiny'))"
RUN micromamba run -n voicebot python -c "import os; m=os.getenv('COQUI_TTS_MODEL'); \
    (print('No TTS cache') if not m else __import__('TTS.utils.manage').utils.manage.ModelManager().download_model(m))"

WORKDIR /app
COPY . /app
# ensure package + perms
RUN [ -f app/__init__.py ] || touch app/__init__.py
RUN chown -R mambauser:mambauser /home/mambauser /app

USER mambauser
EXPOSE 8080
CMD ["uvicorn","app.server:app","--host","0.0.0.0","--port","8080","--proxy-headers","--forwarded-allow-ips=*"]
