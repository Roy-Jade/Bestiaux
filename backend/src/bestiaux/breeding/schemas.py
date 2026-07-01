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
