from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.ingredient import IngredientResponse

class FavoriteCombinationItemResponse(BaseModel):
    ingredient: IngredientResponse
    model_config = ConfigDict(from_attributes=True)

class FavoriteCombinationBase(BaseModel):
    name: str | None = None
    ingredient_key: str

class FavoriteCombinationCreate(FavoriteCombinationBase):
    ingredient_ids: list[int]

class FavoriteCombinationResponse(FavoriteCombinationBase):
    id: int
    user_id: int
    created_at: datetime
    items: list[FavoriteCombinationItemResponse]
    model_config = ConfigDict(from_attributes=True)
