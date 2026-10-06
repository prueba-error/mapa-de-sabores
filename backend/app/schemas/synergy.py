from pydantic import BaseModel, Field


class EvaluatePairingsRequest(BaseModel):
    ingredient_ids: list[int] = Field(min_length=2, max_length=10)


class CoverageInfo(BaseModel):
    pairs_with_data: int
    pairs_total: int


class ClashingIngredient(BaseModel):
    ingredient_id: int
    avg_affinity: float


class SynergyEvaluationResponse(BaseModel):
    synergy_score: int | None
    coverage: CoverageInfo
    pairwise_matrix: list[list[float | None]]
    clashing_ingredients: list[ClashingIngredient]
