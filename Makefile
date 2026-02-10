.PHONY: install test lint format check docs

install:
	pip install -e ./engine[dev]

test:
	pytest engine/tests/ -v

lint:
	ruff check engine/
	ruff format --check engine/

format:
	ruff format engine/
	ruff check --fix engine/

check: lint test

docs:
	mkdocs serve
