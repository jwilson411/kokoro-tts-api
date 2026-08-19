"""TTS engines.

Live engine wraps kokoro.KPipeline and downloads weights from Hugging Face
on first use. Stub engine writes a short silent WAV so CI can boot the app
without a 400MB model pull.
"""

from __future__ import annotations

import io
import os
import wave
from dataclasses import dataclass

from app.voices import SAMPLE_RATE


@dataclass(frozen=True)
class SynthResult:
    wav_bytes: bytes
    duration_seconds: float
    voice: str
    sample_rate: int = SAMPLE_RATE


class Engine:
    name = "base"

    def synthesize(self, text: str, voice: str, speed: float) -> SynthResult:
        raise NotImplementedError


def _silent_wav(seconds: float = 0.25, sample_rate: int = SAMPLE_RATE) -> bytes:
    nframes = max(1, int(sample_rate * seconds))
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(b"\x00\x00" * nframes)
    return buf.getvalue()


class StubEngine(Engine):
    name = "stub"

    def synthesize(self, text: str, voice: str, speed: float) -> SynthResult:
        # Duration tracks input length so tests can assert a real contract
        # without loading Kokoro. Cap so CI stays fast.
        seconds = min(0.5, 0.05 + (len(text) / 2000.0))
        wav = _silent_wav(seconds=seconds)
        return SynthResult(wav_bytes=wav, duration_seconds=round(seconds, 3), voice=voice)


class KokoroEngine(Engine):
    name = "kokoro"

    def __init__(self) -> None:
        from kokoro import KPipeline

        self._pipeline = KPipeline(lang_code="a")

    def synthesize(self, text: str, voice: str, speed: float) -> SynthResult:
        import numpy as np
        import soundfile as sf

        chunks = []
        for _, _, audio in self._pipeline(text, voice=voice, speed=speed):
            chunks.append(audio)
        if not chunks:
            raise RuntimeError("kokoro returned no audio")
        combined = np.concatenate(chunks)
        duration = float(len(combined) / SAMPLE_RATE)
        buf = io.BytesIO()
        sf.write(buf, combined, SAMPLE_RATE, format="WAV")
        return SynthResult(
            wav_bytes=buf.getvalue(),
            duration_seconds=round(duration, 3),
            voice=voice,
        )


def build_engine() -> Engine:
    if os.environ.get("KOKORO_STUB") == "1":
        return StubEngine()
    return KokoroEngine()


def wav_looks_valid(data: bytes) -> bool:
    if len(data) < 44:
        return False
    return data[:4] == b"RIFF" and data[8:12] == b"WAVE"
