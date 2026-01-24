"""Transaction model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    from_type: Mapped[str] = mapped_column(String(20), nullable=False)
    from_id: Mapped[str] = mapped_column(String(50), nullable=False)
    to_type: Mapped[str] = mapped_column(String(20), nullable=False)
    to_id: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    tx_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "from_type": self.from_type,
            "from_id": self.from_id,
            "to_type": self.to_type,
            "to_id": self.to_id,
            "amount": self.amount,
            "tx_type": self.tx_type,
            "description": self.description or "",
        }
