# Contributing to xarray_plotly

Thanks for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/FBumann/xarray_plotly.git
cd xarray_plotly

# Install with dev dependencies
uv sync --extra dev

# Install pre-commit hooks
uv run pre-commit install
```

## Running Tests

```bash
uv run pytest
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for linting and formatting. Pre-commit hooks will run automatically, or you can run manually:

```bash
uv run ruff check --fix .
uv run ruff format .
```

## Making Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run tests (`uv run pytest`)
5. Commit your changes
6. Push to your fork and open a Pull Request

## Releases

Releases are fully automated via [Release Please](https://github.com/googleapis/release-please).

1. Merge PRs to `main` using [conventional commit](https://www.conventionalcommits.org/) prefixes (`feat:`, `fix:`, etc.)
2. Release Please automatically creates/updates a release PR with changelog and version bump
3. Merge the release PR to publish to PyPI and deploy updated docs
