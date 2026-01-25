"""User model."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, now_local

if TYPE_CHECKING:
    from .perk import UserPerk


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    player_uuid: Mapped[str] = mapped_column(String(8), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    profession: Mapped[str | None] = mapped_column(String(100), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, default=100)
    band: Mapped[str | None] = mapped_column(String(100), nullable=True)
    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at = mapped_column(DateTime, default=now_local)

    user_perks: Mapped[list["UserPerk"]] = relationship("UserPerk", back_populates="user")

    def __str__(self) -> str:
        return f"{self.name} ({self.player_uuid})"

    def to_dict(self) -> dict:
        return {
            "user_id": self.telegram_id,
            "player_uuid": self.player_uuid,
            "name": self.name,
            "profession": self.profession or "",
            "balance": self.balance,
            "band": self.band or "",
            "attributes": self.attributes or {},
        }
