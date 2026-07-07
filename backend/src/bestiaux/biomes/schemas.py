from pydantic import BaseModel


class BiomeResponse(BaseModel):
    id: str
    name: str
    description: str
