import os

os.environ["KOKORO_STUB"] = "1"

from fastapi.testclient import TestClient

from app.engine import wav_looks_valid
from app.main import app, get_engine
from app.voices import DEFAULT_VOICE, MAX_TEXT_CHARS


def setup_module() -> None:
    get_engine.cache_clear()


client = TestClient(app)


def test_health_reports_stub() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["engine"] == "stub"
    assert body["default_voice"] == DEFAULT_VOICE
    assert body["voices"] > 0


def test_voices_includes_default() -> None:
    r = client.get("/voices")
    assert r.status_code == 200
    assert DEFAULT_VOICE in r.json()


def test_tts_returns_wav() -> None:
    r = client.post("/tts", json={"text": "Hello from CI."})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("audio/wav")
    assert wav_looks_valid(r.content)
    assert r.headers["X-Voice"] == DEFAULT_VOICE


def test_unknown_voice_is_400() -> None:
    r = client.post("/tts", json={"text": "hi", "voice": "not_a_voice"})
    assert r.status_code == 400
    assert "unknown voice" in r.json()["detail"]


def test_empty_text_is_422() -> None:
    r = client.post("/tts", json={"text": ""})
    assert r.status_code == 422


def test_overlong_text_is_422() -> None:
    r = client.post("/tts", json={"text": "x" * (MAX_TEXT_CHARS + 1)})
    assert r.status_code == 422
