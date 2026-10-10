from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Tuple

from app.database import get_db
from app.models.pairing import FlavorPairing
from app.models.ingredient import Ingredient
from app.schemas.synergy import EvaluatePairingsRequest, SynergyEvaluationResponse
from app.services.synergy import calculate_synergy

router = APIRouter(tags=["pairings"])

@router.post("/pairings/evaluate", response_model=SynergyEvaluationResponse)
async def evaluate_pairings(
    request: EvaluatePairingsRequest,
    db: AsyncSession = Depends(get_db)
):
    ingredient_ids = request.ingredient_ids
    
    # Check if ingredients exist
    query = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
    result = await db.execute(query)
    found_ingredients = result.scalars().all()
    
    if len(found_ingredients) != len(set(ingredient_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more ingredients not found"
        )
        
    # Get all pairings between the requested ingredients
    pairings_query = select(FlavorPairing).where(
        FlavorPairing.ingredient_a_id.in_(ingredient_ids),
        FlavorPairing.ingredient_b_id.in_(ingredient_ids)
    )
    pairings_result = await db.execute(pairings_query)
    pairings = pairings_result.scalars().all()
    
    known_pairings: Dict[Tuple[int, int], float] = {}
    for p in pairings:
        a = min(p.ingredient_a_id, p.ingredient_b_id)
        b = max(p.ingredient_a_id, p.ingredient_b_id)
        known_pairings[(a, b)] = p.affinity_score
        
    return calculate_synergy(ingredient_ids, known_pairings)
