# Kokoro TTS API

A small FastAPI wrapper around [Kokoro-82M](https://github.com/hexgrad/kokoro). You send text. You get a WAV. The model runs on the machine that hosts the process. Weights stay on disk after the first Hugging Face download. They are not in this repo.

This is a production-shaped wrapper, not a research notebook. Voice names are allowlisted. Request text is capped. The server will not write audio to an arbitrary filesystem path.

## What it proves

Local inference behind a real HTTP contract. Pinned `kokoro` / `misaki` versions (0.9.x breaks `EspeakWrapper`). A CI path that boots the app without downloading 400MB of weights.

## Quick start

```bash
# system phonemizer (required)
sudo apt-get install -y espeak-ng   # or: brew install espeak-ng

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m app.main
```

First real request downloads Kokoro-82M from Hugging Face (~400MB). Later requests stay local.

```bash
curl http://127.0.0.1:8765/health

curl http://127.0.0.1:8765/voices

curl -X POST http://127.0.0.1:8765/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello from a local box.","voice":"am_michael"}' \
  --output hello.wav
```

Docker:

```bash
docker build -t kokoro-tts-api .
docker run --rm -p 8765:8765 \
  -v kokoro-hf:/root/.cache/huggingface \
  kokoro-tts-api
docker compose up --build
```

## API

| Method | Path | Notes |
|---|---|---|
| `GET` | `/health` | Process is up. Reports stub vs live engine. |
| `GET` | `/voices` | Allowlisted voices. |
| `POST` | `/tts` | JSON body. Returns `audio/wav`. |

While the process is up, FastAPI also serves the OpenAPI UI at `/docs`.

`POST /tts` body:

| Field | Type | Default | Limits |
|---|---|---|---|
| `text` | string | required | 1–8000 characters |
| `voice` | string | `am_michael` | must be in `/voices` |
| `speed` | float | `1.0` | 0.5–2.0 |

There is no "save this file wherever I tell you" endpoint. A public TTS wrapper that writes caller-chosen paths is a remote write primitive.

### Limits

Request text is capped at 8000 characters. `POST /tts` is also rate limited to 30 requests per minute per process by default. Requests over the limit get HTTP 429 with a `Retry-After` header. Set `KOKORO_RATE_LIMIT` to change the limit; a value of 0 disables it.

## Config

| Env | Default | Meaning |
|---|---|---|
| `KOKORO_HOST` | `127.0.0.1` | Bind address. Docker image sets `0.0.0.0`. |
| `KOKORO_PORT` | `8765` | Port |
| `KOKORO_VOICE` | `am_michael` | Default voice |
| `KOKORO_RATE_LIMIT` | `30` | Requests per minute for `POST /tts`. 0 or negative disables the limit. Text stays capped at 8000 characters regardless. |
| `KOKORO_STUB` | unset | `1` uses a silent stub engine. Used by CI. |

Copy `.env.example` and export the values you want to change. `.env` is gitignored.

## Versions

| Package | Pin | Why |
|---|---|---|
| [kokoro](https://github.com/hexgrad/kokoro) | 0.7.x (`>=0.7.4,<0.8`) | 0.9.x depends on a misaki release that removed `EspeakWrapper.set_data_path()`. |
| misaki | 0.7.x (`>=0.7.4,<0.8`) | Same 0.9 break. Stay on 0.7.x until that API is stable. |

These pins match `requirements.txt`. Do not bump past 0.7.x.

## Tests

```bash
make test
```

CI runs the same command. Tests never import the real Kokoro package. They exercise validation, the allowlist, and a WAV header from the stub.

## What this repo does not contain

- Model weights (`.onnx`, `.pt`, voice bins)
- Vault paths, cron wrappers, or article extractors
- An endpoint that reads or writes arbitrary host files

Weights come from [`hexgrad/Kokoro-82M`](https://huggingface.co/hexgrad/Kokoro-82M) on first live run. Kokoro itself is Apache 2.0.

## License

MIT for this wrapper. Kokoro-82M remains Apache 2.0 under hexgrad.
