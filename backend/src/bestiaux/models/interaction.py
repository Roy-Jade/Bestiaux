import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bestiaux.models.base import Base


class InteractionType(enum.StrEnum):
    FEED = "FEED"
    PLAY = "PLAY"
    HEAL = "HEAL"
    TRAIN = "TRAIN"


class TrainTarget(enum.StrEnum):
    FORCE = "FORCE"
    BEAUTY = "BEAUTY"
    SIZE = "SIZE"


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    creature_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("creatures.id"), index=True)
    type: Mapped[InteractionType] = mapped_column(Enum(InteractionType))
    train_target: Mapped[TrainTarget | None] = mapped_column(Enum(TrainTarget), default=None)
    mentor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("creatures.id"), default=None)
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    creature: Mapped[Creature] = relationship(  # noqa: F821
        back_populates="interactions", foreign_keys=[creature_id]
    )
    mentor: Mapped[Creature | None] = relationship(foreign_keys=[mentor_id])  # noqa: F821
