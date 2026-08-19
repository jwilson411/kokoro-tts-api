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

# Cache HF weights outside the image. Mount a volume at /root/.cache/huggingface.
CMD ["python", "-m", "app.main"]
