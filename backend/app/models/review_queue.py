from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


class PairingReviewQueue(Base):
    __tablename__ = "pairing_review_queue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingredient_a_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_b_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    suggested_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
    )
    ai_rationale: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )
    flag_reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="pending_review",
        default="pending_review",
        nullable=False,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    ingredient_a: Mapped["Ingredient"] = relationship(
        "Ingredient",
        foreign_keys=[ingredient_a_id],
    )
    ingredient_b: Mapped["Ingredient"] = relationship(
        "Ingredient",
        foreign_keys=[ingredient_b_id],
    )

    __table_args__ = (
        CheckConstraint(
            "ingredient_a_id < ingredient_b_id",
            name="chk_review_ordered_pair",
        ),
        CheckConstraint(
            "status IN ('pending_review', 'approved', 'rejected')",
            name="chk_review_status",
        ),
        Index("idx_review_queue_status", "status"),
    )
