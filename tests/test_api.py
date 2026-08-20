import os

os.environ["KOKORO_STUB"] = "1"

from fastapi.testclient import TestClient

from app.engine import wav_looks_valid
from app.main import app, get_engine, get_limiter
from app.voices import DEFAULT_VOICE, MAX_TEXT_CHARS, VOICES


def setup_module() -> None:
    get_engine.cache_clear()


def setup_function() -> None:
    os.environ.pop("KOKORO_RATE_LIMIT", None)
    get_limiter.cache_clear()


def _set_rate_limit(value: str) -> None:
    os.environ["KOKORO_RATE_LIMIT"] = value
    get_limiter.cache_clear()


client = TestClient(app)


def test_health_reports_stub() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["engine"] == "stub"
    assert body["default_voice"] == DEFAULT_VOICE
    assert body["voices"] > 0


def test_health_key_contract_is_frozen() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert set(r.json()) == {"status", "engine", "default_voice", "voices"}


def test_voices_matches_allowlist_exactly() -> None:
    r = client.get("/voices")
    assert r.status_code == 200
    assert r.json() == VOICES


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


def test_tts_succeeds_under_default_rate_limit() -> None:
    r = client.post("/tts", json={"text": "one request is fine"})
    assert r.status_code == 200


def test_tts_over_rate_limit_is_429() -> None:
    _set_rate_limit("2")
    for _ in range(2):
        assert client.post("/tts", json={"text": "hi"}).status_code == 200
    r = client.post("/tts", json={"text": "hi"})
    assert r.status_code == 429
    assert "rate limit" in r.json()["detail"]
    assert int(r.headers["Retry-After"]) >= 1


def test_rate_limit_zero_disables_limit() -> None:
    _set_rate_limit("0")
    for _ in range(5):
        assert client.post("/tts", json={"text": "hi"}).status_code == 200


def test_rate_limit_does_not_affect_health_and_voices() -> None:
    _set_rate_limit("1")
    assert client.post("/tts", json={"text": "hi"}).status_code == 200
    assert client.post("/tts", json={"text": "hi"}).status_code == 429
    assert client.get("/health").status_code == 200
    assert client.get("/voices").status_code == 200
