# Contributing to line-noder

## Setup

```bash
git clone https://github.com/daudee215/line-noder
cd line-noder
uv sync --extra dev
```

## Running tests

```bash
uv run pytest tests/ -v
uv run pytest tests/integration -v
```

## Code style

```bash
uv run ruff check .
uv run mypy --strict src
```

## Submitting changes

1. Fork the repo.
2. Create a feature branch: `git checkout -b feat/your-feature`.
3. Write tests for new behaviour.
4. Ensure all gates pass locally.
5. Open a pull request against `main`.

## Benchmarks

```bash
uv run pytest benchmark/ --benchmark-only -v
```

Report results in your PR description if you change algorithmic complexity.
