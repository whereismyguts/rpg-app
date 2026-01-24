"""Item model."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .trader import Trader


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    trader_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("traders.id"), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    trader: Mapped["Trader | None"] = relationship("Trader", back_populates="items")

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description or "",
            "price": self.price,
            "trader_id": self.trader.trader_id if self.trader else None,
            "image_url": self.image_url or "",
        }
