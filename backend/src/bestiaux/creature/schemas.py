import uuid
from datetime import datetime

from pydantic import BaseModel

from bestiaux.models.creature import DeathCause, LifeStage


class CreateCreatureRequest(BaseModel):
    name: str


class InteractRequest(BaseModel):
    action: str  # "feed", "play", "heal"


class SetNameRequest(BaseModel):
    name: str


class SetBiomeRequest(BaseModel):
    biome_id: str


class CreatureResponse(BaseModel):
    id: uuid.UUID
    name: str
    life_stage: LifeStage
    biome_id: str | None
    generation: int
    is_alive: bool
    death_cause: DeathCause | None
    max_stage_reached: LifeStage

    autonomy: float
    hunger: float
    health: float
    happiness: float

    training_force: float
    training_beauty: float
    training_size: float

    time_frozen: bool
    created_at: datetime | None
