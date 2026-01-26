"""Item model."""

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, now_local

if TYPE_CHECKING:
    from .trader import Trader
    from .user import User


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    trader_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("traders.id"), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    # temporary effect fields
    effect_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    effect_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    effect_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)  # minutes

    trader: Mapped["Trader | None"] = relationship("Trader", back_populates="items")

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description or "",
            "price": self.price,
            "trader_id": self.trader.trader_id if self.trader else None,
            "image_url": self.image_url or "",
            "effect_type": self.effect_type or "",
            "effect_value": self.effect_value or 0,
            "effect_duration": self.effect_duration or 0,
        }


class ActiveEffect(Base):
    """Tracks active temporary effects on users."""
    __tablename__ = "active_effects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"))
    effect_type: Mapped[str] = mapped_column(String(50), nullable=False)
    effect_value: Mapped[int] = mapped_column(Integer, nullable=False)
    applied_at = mapped_column(DateTime, default=now_local)
    expires_at = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="active_effects")
    item: Mapped["Item"] = relationship("Item")
