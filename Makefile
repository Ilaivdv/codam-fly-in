.PHONY: install run help visual debug clean lint lint-strict
.DEFAULT_GOAL: run
PY = python3

FLAKE8 = uv run $(PY) -m flake8 src
MYPY = uv run $(PY) -m mypy .
MYPYFLAGS = --warn-return-any \
	--warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs \
	--disallow-subclassing-any

run: install
	@uv run --quiet $(PY) -m src

test:
	@uv run pytest -v tests

help:
	@uv run --quiet $(PY) -m src -h

debug: install
	uv run $(PY) -m pdb -m src

install:
	@uv sync

lint:
	-@$(FLAKE8)
	-@$(MYPY) $(MYPYFLAGS)

lint-strict:
	-@$(FLAKE8)
	-@$(MYPY) --strict

clean:
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	-find . -type d -name ".mypy_cache" -exec rm -rf {} +
	-find . -type d -name ".pytest_cache" -exec rm -rf {} +
