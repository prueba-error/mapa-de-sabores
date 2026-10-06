from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.pairing import FlavorPairing


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    flavor_profile: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    category: Mapped[Optional["Category"]] = relationship(
        "Category",
        back_populates="ingredients",
    )

    pairings_as_a: Mapped[list["FlavorPairing"]] = relationship(
        "FlavorPairing",
        foreign_keys="FlavorPairing.ingredient_a_id",
        back_populates="ingredient_a",
        cascade="all, delete-orphan",
    )
    pairings_as_b: Mapped[list["FlavorPairing"]] = relationship(
        "FlavorPairing",
        foreign_keys="FlavorPairing.ingredient_b_id",
        back_populates="ingredient_b",
        cascade="all, delete-orphan",
    )
