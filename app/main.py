"""HTTP entrypoint."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.engine import Engine, build_engine
from app.voices import DEFAULT_VOICE, MAX_TEXT_CHARS, VOICES, known_voice

HOST = os.environ.get("KOKORO_HOST", "127.0.0.1")
PORT = int(os.environ.get("KOKORO_PORT", "8765"))
DEFAULT = os.environ.get("KOKORO_VOICE", DEFAULT_VOICE)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return build_engine()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Touch the engine so /health can report stub vs live after boot.
    get_engine()
    yield


app = FastAPI(
    title="Kokoro TTS API",
    description="Local text-to-speech via Kokoro-82M. Weights are not in this repo.",
    version="1.0.0",
    lifespan=lifespan,
)


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_CHARS)
    voice: str = Field(default=DEFAULT)
    speed: float = Field(default=1.0, ge=0.5, le=2.0)


class HealthResponse(BaseModel):
    status: str
    engine: str
    default_voice: str
    voices: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    engine = get_engine()
    return HealthResponse(
        status="ok",
        engine=engine.name,
        default_voice=DEFAULT,
        voices=len(VOICES),
    )


@app.get("/voices")
def voices() -> dict[str, str]:
    return VOICES


@app.post("/tts")
def tts(req: TTSRequest) -> Response:
    if not known_voice(req.voice):
        raise HTTPException(status_code=400, detail=f"unknown voice: {req.voice}")
    try:
        result = get_engine().synthesize(req.text, req.voice, req.speed)
    except Exception as exc:  # noqa: BLE001 - surface engine failures as 500
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(
        content=result.wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Voice": result.voice,
            "X-Duration-Seconds": str(result.duration_seconds),
            "X-Sample-Rate": str(result.sample_rate),
        },
    )


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()
