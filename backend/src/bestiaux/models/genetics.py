import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bestiaux.models.base import Base


class TraitCategory(enum.StrEnum):
    EYES = "EYES"
    SKULL_TOP = "SKULL_TOP"
    DORSAL = "DORSAL"
    CAUDAL = "CAUDAL"
    COLOR = "COLOR"


class Allele(Base):
    __tablename__ = "alleles"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    trait_category: Mapped[TraitCategory] = mapped_column(Enum(TraitCategory))
    name: Mapped[str] = mapped_column(String(100))
    is_dominant: Mapped[bool] = mapped_column(default=False)
    sprite_key: Mapped[str] = mapped_column(String(200))


class CreatureGenome(Base):
    __tablename__ = "creature_genomes"

    creature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("creatures.id"), primary_key=True)
    trait_category: Mapped[TraitCategory] = mapped_column(Enum(TraitCategory), primary_key=True)
    allele_from_parent1: Mapped[str] = mapped_column(ForeignKey("alleles.id"))
    allele_from_parent2: Mapped[str] = mapped_column(ForeignKey("alleles.id"))
    expressed_allele: Mapped[str] = mapped_column(ForeignKey("alleles.id"))

    creature: Mapped[Creature] = relationship(back_populates="genome")  # noqa: F821
    allele_p1: Mapped[Allele] = relationship(foreign_keys=[allele_from_parent1])
    allele_p2: Mapped[Allele] = relationship(foreign_keys=[allele_from_parent2])
    allele_expressed: Mapped[Allele] = relationship(foreign_keys=[expressed_allele])


class WildGenePool(Base):
    __tablename__ = "wild_gene_pool"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    allele_id: Mapped[str] = mapped_column(ForeignKey("alleles.id"), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="wild_gene_pool")  # noqa: F821
    allele: Mapped[Allele] = relationship()
