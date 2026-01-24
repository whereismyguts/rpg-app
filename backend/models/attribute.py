"""Attribute config model."""

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Attribute(Base):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_value: Mapped[int] = mapped_column(Integer, default=10)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "attribute_name": self.attribute_name,
            "display_name": self.display_name,
            "max_value": self.max_value,
            "description": self.description or "",
        }
