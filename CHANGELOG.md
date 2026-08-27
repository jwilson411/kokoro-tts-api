# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- In-process rate limit for `POST /tts` (default 30 req/min; `KOKORO_RATE_LIMIT`; 429 + `Retry-After`)
- `.dockerignore` so git, tests, caches, venvs, and weights stay out of the image context
- Dockerfile `HEALTHCHECK` on `/health` via stdlib urllib
- Ruff lint-only CI job (`ruff check`; no format)
- CONTRIBUTING.md (stub tests vs live engine; live tests are not in CI)
- README versions table: kokoro/misaki 0.7.x; 0.9.x breaks `EspeakWrapper.set_data_path()`
- SECURITY.md (default bind `127.0.0.1`; Docker `0.0.0.0`; WAV in the response, no caller-chosen path)
- `compose.yml` on port 8765 with a host Hugging Face cache bind
- stdlib `examples/client.py` (health, voices, tts to `hello.wav`)
- Python 3.11 and 3.12 stub-test matrix (ruff stays on 3.12)
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1; report via GitHub private advisory)
- Pull request template (stub tests, no weights, no secrets)
- Dependabot weekly pip + github-actions (ignore kokoro/misaki `>=0.8`)

### Tests

- Freeze `/health` and `/voices` JSON key contract
- Form/multipart `POST /tts` returns 422, not 500

## [1.0.0] - 2026-08-19

### Added

- Public FastAPI wrapper around local Kokoro-82M
- Allowlisted voices, 8000-character text cap, WAV in the HTTP response
- Stub engine (`KOKORO_STUB=1`) so CI boots without downloading weights
- Weights stay on disk after the first Hugging Face download; they are not in this repo

[Unreleased]: https://github.com/jwilson411/kokoro-tts-api/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/jwilson411/kokoro-tts-api/releases/tag/v1.0.0
