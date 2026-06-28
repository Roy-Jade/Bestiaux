# Bestiaux — Claude Code Guidelines

## Project structure

Monorepo with `frontend/` (React + TypeScript + Pixi.js) and `backend/` (FastAPI + SQLAlchemy async + PostgreSQL).

## Commands

### Backend (run from `backend/`)
- `uv sync` — install dependencies
- `uv run fastapi dev src/bestiaux/main.py` — start dev server
- `uv run pytest` — run all tests
- `uv run pytest tests/unit/` — run unit tests only
- `uv run ruff check src/` — lint
- `uv run ruff format src/` — format

### Frontend (run from `frontend/`)
- `pnpm install` — install dependencies
- `pnpm dev` — start dev server
- `pnpm build` — production build
- `npx tsc --noEmit` — type-check
- `npx eslint src/` — lint
- `npx prettier --write src/` — format

### Infrastructure
- `docker compose up -d` — start PostgreSQL
- `docker compose down` — stop PostgreSQL

## Code standards

- **TypeScript strict**: no `any`, ever. Use `unknown` and narrow.
- **Python**: Ruff for lint and format, follow PEP 8.
- **SOLID, DRY, YAGNI**: clean code, but readability first.
- **TDD**: write tests before implementation.
- **Tests pattern**: AAA (GIVEN / WHEN / THEN).
- **No comments** unless the WHY is non-obvious.

## Architecture rules

### Backend — Clean Architecture (feature-based)
Each feature has 6 files: `router.py`, `schemas.py`, `service.py`, `domain.py`, `repository.py`, `protocols.py`.

- **domain.py**: pure Python dataclasses, no framework imports. Business rules live here.
- **service.py**: orchestrates use cases, depends on Protocols (never on SQLAlchemy directly).
- **repository.py**: implements Protocols with SQLAlchemy. Converts between domain entities and ORM models.
- **protocols.py**: abstract interfaces (typing.Protocol) for repositories.
- **router.py**: HTTP layer only. Uses FastAPI Depends() for injection.
- **schemas.py**: Pydantic models for API request/response validation.

Models are centralized in `models/` (SQLAlchemy models are coupled by nature).

### Frontend — Feature-based
Code is organized under `src/functions/<feature>/` with `pages/` and `components/` subdirectories.
Shared code lives in `src/api/`, `src/hooks/`, `src/types/`, `src/stores/`.

## Game constants

Phase durations: baby=1h, child=2d, adolescent=3d, young_adult=infinite.
Training thresholds: visual steps at 25/50/75/100.
Max reproductions per adult: 5.
Genetic traits: EYES, SKULL_TOP, DORSAL, CAUDAL, COLOR.
