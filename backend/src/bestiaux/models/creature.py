import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bestiaux.models.base import Base


class LifeStage(enum.StrEnum):
    BABY = "BABY"
    CHILD = "CHILD"
    ADOLESCENT = "ADOLESCENT"
    YOUNG_ADULT = "YOUNG_ADULT"
    ADULT = "ADULT"


class DeathCause(enum.StrEnum):
    STARVATION = "STARVATION"
    DISEASE = "DISEASE"
    ESCAPE = "ESCAPE"


class Creature(Base):
    __tablename__ = "creatures"

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    life_stage: Mapped[LifeStage] = mapped_column(Enum(LifeStage), default=LifeStage.BABY)
    stage_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    biome_id: Mapped[str | None] = mapped_column(ForeignKey("biomes.id"), default=None)
    parent1_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creatures.id"), default=None)
    parent2_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creatures.id"), default=None)
    generation: Mapped[int] = mapped_column(default=1)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_alive: Mapped[bool] = mapped_column(default=True)
    death_cause: Mapped[DeathCause | None] = mapped_column(Enum(DeathCause), default=None)
    max_stage_reached: Mapped[LifeStage] = mapped_column(Enum(LifeStage), default=LifeStage.BABY)

    autonomy: Mapped[float] = mapped_column(Float, default=0.0)
    hunger: Mapped[float] = mapped_column(Float, default=100.0)
    health: Mapped[float] = mapped_column(Float, default=100.0)
    happiness: Mapped[float] = mapped_column(Float, default=100.0)

    training_force: Mapped[float] = mapped_column(Float, default=0.0)
    training_beauty: Mapped[float] = mapped_column(Float, default=0.0)
    training_size: Mapped[float] = mapped_column(Float, default=0.0)

    reproduction_count: Mapped[int] = mapped_column(default=0)
    last_interaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    time_frozen: Mapped[bool] = mapped_column(default=False)
    freeze_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), default=None
    )

    # Daily cycle
    is_asleep: Mapped[bool] = mapped_column(default=False)
    woke_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    went_to_sleep_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    # Training
    trainings_done_today: Mapped[int] = mapped_column(default=0)
    last_trained_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    pending_training_force: Mapped[float] = mapped_column(Float, default=0.0)
    pending_training_beauty: Mapped[float] = mapped_column(Float, default=0.0)
    pending_training_size: Mapped[float] = mapped_column(Float, default=0.0)

    # Mentor
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creatures.id"), default=None)
    mentor_since: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped[User] = relationship(back_populates="creatures")  # noqa: F821
    biome: Mapped[Biome | None] = relationship()  # noqa: F821
    parent1: Mapped[Creature | None] = relationship(
        foreign_keys=[parent1_id], remote_side="Creature.id"
    )
    parent2: Mapped[Creature | None] = relationship(
        foreign_keys=[parent2_id], remote_side="Creature.id"
    )
    mentor: Mapped[Creature | None] = relationship(
        foreign_keys=[mentor_id], remote_side="Creature.id"
    )
    genome: Mapped[list[CreatureGenome]] = relationship(back_populates="creature")  # noqa: F821
    interactions: Mapped[list[InteractionLog]] = relationship(  # noqa: F821
        back_populates="creature", foreign_keys="InteractionLog.creature_id"
    )
