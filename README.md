# Bestiaux

Jeu navigateur d'élevage de créatures. Élevez votre bestiau, faites-le évoluer à travers plusieurs étapes de vie, puis donnez-lui une descendance et recommencez.

## Concept

Bestiaux est un jeu inspiré des tamagotchis : le joueur s'occupe d'une créature (nourrir, jouer, soigner) et la guide à travers ses étapes de vie — bébé, enfant, adolescent, jeune adulte, adulte. Chaque génération hérite des traits génétiques de ses parents via un système de dominance/récessivité, et l'apparence est influencée par le biome d'élevage et l'entraînement choisi.

### Mécaniques principales

- **Cycle de vie** : bébé (1h) → enfant (2j) → adolescent (3j) → jeune adulte (∞) → adulte
- **Soins** : nourrir, jouer, soigner — la régularité augmente l'autonomie du bestiau
- **Génétique** : 5 traits (yeux, crâne, dos, queue, couleur) avec système dominant/récessif
- **Biomes** : l'environnement d'élevage détermine la famille du bestiau (marin, montagnard...)
- **Entraînement** : 3 styles combinables (force, beauté, taille) avec système de mentorat
- **Reproduction** : croisez vos bestiaux adultes ou utilisez des géniteurs sauvages
- **Compendium** : collectionnez toutes les variations possibles

## Stack technique

| Couche | Technologies |
|---|---|
| Frontend | React, TypeScript (strict), Pixi.js, Vite |
| Backend | FastAPI, SQLAlchemy (async), Pydantic |
| Base de données | PostgreSQL |
| Tooling | pnpm, uv, Ruff, ESLint, Prettier, pre-commit |
| Tests | Vitest, React Testing Library, Playwright, pytest |

## Architecture

Monorepo avec Clean Architecture feature-based :

```
bestiaux/
├── frontend/          # React + Pixi.js
│   └── src/functions/  # Organisation par feature (core, creature, breeding...)
├── backend/           # FastAPI
│   └── src/bestiaux/   # Organisation par feature avec pattern 6 fichiers
│       └── <feature>/  # router, schemas, service, domain, repository, protocols
├── docs/              # Documentation (MCD...)
└── docker-compose.yml # PostgreSQL local
```

Chaque feature backend suit le pattern Clean Architecture :
- **router** — couche HTTP (FastAPI)
- **schemas** — validation request/response (Pydantic)
- **service** — orchestration des use cases
- **domain** — entités pures et règles métier
- **repository** — accès aux données (SQLAlchemy)
- **protocols** — interfaces abstraites pour l'injection de dépendances

## Lancer le projet

### Prérequis

- Node.js 20+
- Python 3.14+
- Docker (pour PostgreSQL)
- pnpm (`npm install -g pnpm`)
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### Base de données

```bash
docker compose up -d
```

### Backend

```bash
cd backend
uv sync
uv run fastapi dev src/bestiaux/main.py
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Qualité de code

- SOLID, DRY, YAGNI, Clean Code
- TypeScript strict (aucun `any`)
- TDD : tests avant implémentation
- Couverture : unitaire, intégration, end-to-end
- Pre-commit hooks : lint + format automatique
