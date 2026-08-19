.PHONY: test run

test:
	KOKORO_STUB=1 python3 -m pytest -q

run:
	python3 -m app.main
