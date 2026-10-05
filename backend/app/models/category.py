from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.ingredient import Ingredient


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    color_code: Mapped[str] = mapped_column(String(7), nullable=False)

    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="category",
    )
