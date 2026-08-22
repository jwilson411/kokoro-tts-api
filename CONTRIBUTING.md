# Contributing

This repo is a FastAPI wrapper. It has no `pyproject.toml`. Install from `requirements.txt`. Do not add a packaging project.

## Setup

Python 3.12. Live synthesis also needs `espeak-ng` on the host.

```bash
sudo apt-get install -y espeak-ng   # or: brew install espeak-ng
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

CI and local stub tests do not install `kokoro` / `misaki`. For those, install the same set CI uses:

```bash
pip install fastapi "uvicorn[standard]" pydantic pytest httpx
```

## Stub tests (what CI runs)

```bash
make test
```

That is `KOKORO_STUB=1 python3 -m pytest -q`. The stub engine writes a short silent WAV. Tests never import the real Kokoro package and never download weights. Lint is `make lint` (`ruff check` only; this repo does not run `ruff format`).

Live tests are not in CI. Do not add a job that pulls Kokoro-82M.

## Live engine (local only)

Unset `KOKORO_STUB` (or leave it unset). Then:

```bash
python3 -m app.main
```

First real `POST /tts` downloads Kokoro-82M from Hugging Face (~400MB) into the local Hugging Face cache. Later requests stay on disk. Default bind is `127.0.0.1:8765`. The Docker image binds `0.0.0.0`.

Do not commit weights (`.onnx`, `.pt`, voice bins) or anything under `~/.cache/huggingface`.

## Changing the API

1. Keep `/health` and `/voices` key contracts unless you are deliberately breaking them and updating the freeze tests.
2. Voice names stay allowlisted. Request text stays capped at 8000 characters.
3. There is no endpoint that writes audio to a caller-chosen path.
4. Add or extend tests under `tests/` and run `make test`.

Open a pull request against `main`. Keep secrets, model weights, and `/mnt/defiant` paths out of the tree.
