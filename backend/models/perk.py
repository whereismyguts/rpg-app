"""Perk and UserPerk models."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, now_local

if TYPE_CHECKING:
    from .user import User


class Perk(Base):
    __tablename__ = "perks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    perk_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    one_time: Mapped[bool] = mapped_column(Boolean, default=False)
    effect_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    effect_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_perks: Mapped[list["UserPerk"]] = relationship("UserPerk", back_populates="perk")

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "perk_id": self.perk_id,
            "name": self.name,
            "description": self.description or "",
            "one_time": self.one_time,
            "effect_type": self.effect_type or "",
            "effect_value": self.effect_value or 0,
            "image_url": self.image_url or "",
        }


class UserPerk(Base):
    __tablename__ = "user_perks"
    __table_args__ = (UniqueConstraint("user_id", "perk_id", name="uq_user_perk"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    perk_id: Mapped[int] = mapped_column(Integer, ForeignKey("perks.id"))
    applied_at = mapped_column(DateTime, default=now_local)

    user: Mapped["User"] = relationship("User", back_populates="user_perks")
    perk: Mapped["Perk"] = relationship("Perk", back_populates="user_perks")
