.PHONY: test run lint

lint:
	ruff check

test:
	KOKORO_STUB=1 python3 -m pytest -q

run:
	python3 -m app.main
