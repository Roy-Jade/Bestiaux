import uuid
from datetime import datetime

from pydantic import BaseModel


class FormEntryResponse(BaseModel):
    form_id: str
    biome_id: str
    level: int
    dominant_stats: list[str]
    discovered: bool
    latest_creature_id: uuid.UUID | None
    latest_creature_name: str | None


class FormsResponse(BaseModel):
    forms: list[FormEntryResponse]


class CreatureSummaryResponse(BaseModel):
    id: uuid.UUID
    name: str
    generation: int
    life_stage: str
    is_alive: bool
    is_active: bool
    biome_id: str | None
    form_id: str | None
    training_force: float
    training_beauty: float
    training_size: float
    max_stage_reached: str
    created_at: datetime | None


class HistoryResponse(BaseModel):
    creatures: list[CreatureSummaryResponse]


class GenomeGeneResponse(BaseModel):
    trait_category: str
    allele_from_parent1: str
    allele_from_parent2: str
    expressed_allele: str


class CreatureDetailResponse(BaseModel):
    id: uuid.UUID
    name: str
    generation: int
    life_stage: str
    is_alive: bool
    biome_id: str | None
    form_id: str | None
    training_force: float
    training_beauty: float
    training_size: float
    autonomy: float
    hunger: float
    health: float
    happiness: float
    genome: list[GenomeGeneResponse]
    parent1_id: uuid.UUID | None
    parent2_id: uuid.UUID | None
    created_at: datetime | None


class AlleleDetailResponse(BaseModel):
    id: str
    trait_category: str
    name: str
    is_dominant: bool
    sprite_key: str


class UnlockedAllelesResponse(BaseModel):
    alleles: list[AlleleDetailResponse]
