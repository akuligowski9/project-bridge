.PHONY: install test lint format check docs build

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

build:
	cp README.md engine/README.md
	cd engine && python -m build
	rm -f engine/README.md
