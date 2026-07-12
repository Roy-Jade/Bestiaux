import uuid
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class OwnedParent(BaseModel):
    type: Literal["creature"]
    id: uuid.UUID


class WildParent(BaseModel):
    type: Literal["wild"]


ParentSource = Annotated[OwnedParent | WildParent, Field(discriminator="type")]


class BreedingRequest(BaseModel):
    parent1: ParentSource
    parent2: ParentSource


class CompatibleCreature(BaseModel):
    id: uuid.UUID
    name: str
    generation: int
    biome_id: str | None
    training_force: float
    training_beauty: float
    training_size: float


class CompatiblePartnersResponse(BaseModel):
    wild_available: bool
    creatures: list[CompatibleCreature]
