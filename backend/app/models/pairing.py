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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


class FlavorPairing(Base):
    __tablename__ = "flavor_pairings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ingredient_a_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_b_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    affinity_score: Mapped[Decimal] = mapped_column(
        Numeric(3, 2),
        nullable=False,
    )
    ai_rationale: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(
        String(30),
        server_default="llm_synthesis",
        default="llm_synthesis",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    ingredient_a: Mapped["Ingredient"] = relationship(
        "Ingredient",
        foreign_keys=[ingredient_a_id],
        back_populates="pairings_as_a",
    )
    ingredient_b: Mapped["Ingredient"] = relationship(
        "Ingredient",
        foreign_keys=[ingredient_b_id],
        back_populates="pairings_as_b",
    )

    __table_args__ = (
        CheckConstraint(
            "ingredient_a_id < ingredient_b_id",
            name="chk_ordered_pair",
        ),
        UniqueConstraint(
            "ingredient_a_id",
            "ingredient_b_id",
            name="uq_ingredient_pair",
        ),
        CheckConstraint(
            "affinity_score >= 0.00 AND affinity_score <= 1.00",
            name="chk_score_range",
        ),
        CheckConstraint(
            "ai_rationale IS NULL OR length(ai_rationale) <= 300",
            name="chk_rationale_len",
        ),
        Index("idx_pairings_b", "ingredient_b_id"),
        Index("idx_pairings_score", affinity_score.desc()),
    )
