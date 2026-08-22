# Security Policy

## Reporting a Vulnerability

Please report security issues through [GitHub's private security advisory form](https://github.com/jwilson411/kokoro-tts-api/security/advisories/new) rather than a public issue. Private advisories give us a chance to fix the problem before it is disclosed.

Include the affected version or commit, steps to reproduce, and what an attacker gains.

## Scope

kokoro-tts-api is a local FastAPI wrapper. The default bind is `127.0.0.1`. The Docker image sets `KOKORO_HOST=0.0.0.0` so the process is reachable on the published port. Treat that as a LAN or reverse-proxy surface, not a public internet default.

The API returns WAV bytes in the HTTP response. It does not write audio to a caller-chosen filesystem path. Voice names are allowlisted. Request text is capped. A live engine may download model weights into the local Hugging Face cache; that path is not caller-controlled.

An attacker who already controls the host, or who can reach a bind you opened on `0.0.0.0` without a network boundary, is outside this wrapper's threat model.

## Supported versions

Only the latest release receives security fixes.
