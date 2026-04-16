# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client library for the AI DIAL platform API (`aidial-client` on PyPI). Provides both sync (`Dial`) and async (`AsyncDial`) clients with typed Pydantic models. Supports Python 3.10-3.13.

## Useful Resources

- OpenAPI specification for the DIAL platform API https://dialx.ai/universal_chat_api.yaml
- DIAL Core GitHub repository: https://github.com/epam/ai-dial-core
- DIAL platform documentation: https://github.com/epam/ai-dial

## Common Commands

```bash
# Setup
make install              # Install dependencies via Poetry

# Testing
make test                 # Run unit tests across Python 3.10-3.13 via nox
make test PYTHON=3.12     # Run tests for a specific Python version
make integration_test     # Run integration tests (requires real API)
make coverage             # Run tests with coverage report

# Run a single test directly
poetry run pytest tests/test_auth.py -k "test_name"

# Linting & formatting
make lint                 # Run all linters (pyright, flake8, codespell, format check)
make format               # Auto-format code (autoflake, isort, black)
```

## Dependency Compatibility Matrix

Tests run against a matrix of dependency versions via nox parametrize (see `noxfile.py`).

All code must work across these versions. The `aidial_client/_compatibility/` module handles Pydantic v1/v2 and OpenAI v1/v2 differences.

## Architecture

### Sync/Async Dual API Pattern

Every public API has both sync and async variants built on a generic base:

- `BaseDialClient[HttpClientT, AuthValueT]` -> `Dial` (sync) / `AsyncDial` (async)
- `BaseResource` / `AsyncResource` for API resource classes
- `SyncHTTPClient` / `AsyncHTTPClient` wrapping httpx

### Key Modules

- `_client.py` - Core client classes
- `_client_pool.py` - Connection pooling (`DialClientPool` / `AsyncDialClientPool`)
- `_auth.py` - Auth handling (API key, Bearer token, callable auth)
- `_http_client/` - HTTP transport layer (sync/async)
- `_exception.py` - Custom exception hierarchy rooted at `DialException`
- `types/` - Pydantic models for all API request/response types
- `resources/` - API resource handler classes
- `_compatibility/` - Pydantic v1/v2 and OpenAI v1/v2 compatibility shims

## PR Checklist

When adding or modifying public API (new resources, methods, types):
- Update `README.md` with usage examples (sync + async) and sample response objects
- Add the new resource to the Client Structure list above
- Export new classes from `resources/__init__.py`
