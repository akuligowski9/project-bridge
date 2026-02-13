.PHONY: install test lint format check docs build scanner-build scanner-test scanner-lint

install:
	pip install -e ./engine[dev]

test:
	python3 -m pytest engine/tests/ -v

lint:
	ruff check engine/
	ruff format --check engine/

format:
	ruff format engine/
	ruff check --fix engine/

scanner-build:
	cargo build --manifest-path scanner/Cargo.toml

scanner-test:
	cargo test --manifest-path scanner/Cargo.toml

scanner-lint:
	cargo fmt --manifest-path scanner/Cargo.toml -- --check
	cargo clippy --manifest-path scanner/Cargo.toml -- -D warnings

check: lint test scanner-lint scanner-test

docs:
	mkdocs serve

build:
	cp README.md engine/README.md
	cd engine && python -m build
	rm -f engine/README.md
