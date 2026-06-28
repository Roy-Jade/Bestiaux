from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from bestiaux.models.base import Base


class Biome(Base):
    __tablename__ = "biomes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    unlocked_by_default: Mapped[bool] = mapped_column(default=True)
