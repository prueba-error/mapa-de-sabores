from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient
    from app.models.user import User


class FavoriteCombination(Base):
    __tablename__ = "favorite_combinations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ingredient_key: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.current_timestamp(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="favorite_combinations",
    )
    items: Mapped[list["FavoriteCombinationItem"]] = relationship(
        "FavoriteCombinationItem",
        back_populates="combination",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "ingredient_key", name="uq_user_combination"),
    )


class FavoriteCombinationItem(Base):
    __tablename__ = "favorite_combination_items"

    combination_id: Mapped[int] = mapped_column(
        ForeignKey("favorite_combinations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    ingredient_id: Mapped[int] = mapped_column(
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        primary_key=True,
    )

    combination: Mapped["FavoriteCombination"] = relationship(
        "FavoriteCombination",
        back_populates="items",
    )
    ingredient: Mapped["Ingredient"] = relationship("Ingredient")
