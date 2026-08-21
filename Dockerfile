FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends espeak-ng libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV KOKORO_HOST=0.0.0.0
ENV KOKORO_PORT=8765
EXPOSE 8765

# Container-internal liveness check: GET /health on the app port, no curl needed.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os,urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('KOKORO_PORT','8765'), timeout=4); sys.exit(0 if r.status==200 else 1)"

# Cache HF weights outside the image. Mount a volume at /root/.cache/huggingface.
CMD ["python", "-m", "app.main"]
