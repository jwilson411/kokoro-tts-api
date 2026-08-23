#!/usr/bin/env python3
"""Tiny stdlib client for kokoro-tts-api.

Run the server, then the client:

    python3 -m app.main
    python3 examples/client.py

Writes hello.wav to the current working directory.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOST = os.environ.get("KOKORO_HOST", "127.0.0.1")
PORT = os.environ.get("KOKORO_PORT", "8765")
BASE = f"http://{HOST}:{PORT}"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def request(path: str, data: bytes | None = None):
    req = urllib.request.Request(BASE + path, data=data)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read(), resp.headers
    except urllib.error.HTTPError as e:
        fail(f"{path} returned HTTP {e.code}")
    except urllib.error.URLError as e:
        fail(f"{path} failed: {e.reason}")


def main() -> None:
    body, _ = request("/health")
    print("/health:", json.dumps(json.loads(body), indent=2))

    body, _ = request("/voices")
    print("/voices:", json.dumps(json.loads(body), indent=2))

    payload = {"text": "Hello from a local box.", "voice": "am_michael"}
    body, headers = request("/tts", data=json.dumps(payload).encode())
    if not body:
        fail("/tts returned an empty body")

    out = Path.cwd() / "hello.wav"
    out.write_bytes(body)
    print("wrote:", out)
    for name in ("Content-Type", "X-Voice"):
        if headers.get(name):
            print(f"{name}: {headers[name]}")


if __name__ == "__main__":
    main()
