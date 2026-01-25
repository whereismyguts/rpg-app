"""Trader model."""

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .item import Item


class Trader(Base):
    __tablename__ = "traders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    balance: Mapped[int] = mapped_column(Integer, default=0)

    items: Mapped[list["Item"]] = relationship("Item", back_populates="trader")

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {
            "trader_id": self.trader_id,
            "name": self.name,
            "balance": self.balance,
        }
