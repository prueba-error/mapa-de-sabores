from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategorySchema(BaseModel):
    id: int
    name: str
    color_code: str
    
    model_config = ConfigDict(from_attributes=True)

class IngredientBase(BaseModel):
    name: str
    description: Optional[str] = None
    
class IngredientResponse(IngredientBase):
    id: int
    category: Optional[CategorySchema] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngredientDetailResponse(IngredientResponse):
    flavor_profile: dict[str, float]

class IngredientPairingResponse(BaseModel):
    neighbor_id: int
    neighbor_name: str
    neighbor_category: Optional[str] = None
    affinity_score: float
    ai_rationale: Optional[str] = None
    mechanism: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
