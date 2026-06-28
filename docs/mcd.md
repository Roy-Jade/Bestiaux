# MCD — Bestiaux V1

```mermaid
erDiagram
    USER {
        UUID id PK
        VARCHAR username UK
        VARCHAR email UK
        VARCHAR password_hash
        INT currency
        TIMESTAMP created_at
    }

    SESSION {
        UUID id PK
        UUID user_id FK
        TIMESTAMP created_at
        TIMESTAMP expires_at
    }

    BIOME {
        VARCHAR id PK
        VARCHAR name
        TEXT description
        BOOL unlocked_by_default
    }

    CREATURE {
        UUID id PK
        UUID owner_id FK
        VARCHAR name
        ENUM life_stage
        TIMESTAMP stage_started_at
        VARCHAR biome_id FK
        UUID parent1_id FK
        UUID parent2_id FK
        INT generation
        BOOL is_active
        BOOL is_alive
        ENUM death_cause
        ENUM max_stage_reached
        FLOAT autonomy
        FLOAT hunger
        FLOAT health
        FLOAT happiness
        FLOAT training_force
        FLOAT training_beauty
        FLOAT training_size
        INT reproduction_count
        TIMESTAMP last_interaction_at
        BOOL time_frozen
        TIMESTAMP freeze_started_at
        TIMESTAMP created_at
    }

    ALLELE {
        VARCHAR id PK
        ENUM trait_category
        VARCHAR name
        BOOL is_dominant
        VARCHAR sprite_key
    }

    CREATURE_GENOME {
        UUID creature_id PK_FK
        ENUM trait_category PK
        VARCHAR allele_from_parent1 FK
        VARCHAR allele_from_parent2 FK
        VARCHAR expressed_allele FK
    }

    WILD_GENE_POOL {
        UUID user_id PK_FK
        VARCHAR allele_id PK_FK
        TIMESTAMP unlocked_at
    }

    INTERACTION_LOG {
        UUID id PK
        UUID creature_id FK
        ENUM type
        ENUM train_target
        UUID mentor_id FK
        TIMESTAMP performed_at
    }

    USER ||--o{ SESSION : "s'authentifie via"
    USER ||--o{ CREATURE : "possède"
    USER ||--o{ WILD_GENE_POOL : "a débloqué"

    CREATURE }o--o| BIOME : "vit dans"
    CREATURE |o--o| CREATURE : "parent1 de"
    CREATURE |o--o| CREATURE : "parent2 de (null=sauvage)"
    CREATURE ||--|{ CREATURE_GENOME : "a pour génome"
    CREATURE ||--o{ INTERACTION_LOG : "reçoit"
    CREATURE |o--o{ INTERACTION_LOG : "mentor dans"

    CREATURE_GENOME }o--|| ALLELE : "allèle parent1"
    CREATURE_GENOME }o--|| ALLELE : "allèle parent2"
    CREATURE_GENOME }o--|| ALLELE : "allèle exprimé"

    WILD_GENE_POOL }o--|| ALLELE : "contient"
```

## Légende des cardinalités

| Relation | Cardinalité | Notes |
|---|---|---|
| USER → SESSION | 1,N | Un user a 0 à N sessions actives |
| USER → CREATURE | 1,N | Un user possède 0 à N bestiaux (vivants + morts) |
| USER → WILD_GENE_POOL | 1,N | Pool qui grandit avec les découvertes |
| CREATURE → BIOME | 0,1 — 1 | Choisi à l'étape Enfant, null avant |
| CREATURE → CREATURE (parent) | 0,1 — 0,1 | Auto-référence, nullable (premier bestiau ou sauvage) |
| CREATURE → CREATURE_GENOME | 1 — 5 | Exactement 5 lignes (1 par trait_category) |
| CREATURE → INTERACTION_LOG | 1,N | Historique de toutes les interactions |
| CREATURE_GENOME → ALLELE | N — 1 | 3 FK par ligne (parent1, parent2, exprimé) |

## Notes de conception

- **Freeze** : au dégel, `stage_started_at` et `last_interaction_at` sont décalés de `(now - freeze_started_at)`. Pas de table de log freeze nécessaire.
- **Lignée** : la consanguinité est vérifiée par parcours de `parent1_id`/`parent2_id` en remontant l'arbre.
- **Compendium** : pas de table dédiée, dérivé par requête sur `CREATURE` (même mortes) + `max_stage_reached`.
- **Training** : paliers visuels à 25/50/75/100 pour force, beauty et size. Les 3 sont combinables.
