from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bestiaux.models.base import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    currency: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    creatures: Mapped[list[Creature]] = relationship(back_populates="owner")  # noqa: F821
    wild_gene_pool: Mapped[list[WildGenePool]] = relationship(back_populates="user")  # noqa: F821
