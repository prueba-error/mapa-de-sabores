from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_, and_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.ingredient import Ingredient
from app.models.pairing import FlavorPairing
from app.schemas.ingredient import (
    IngredientResponse,
    IngredientDetailResponse,
    IngredientPairingResponse,
)

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.get("", response_model=list[IngredientResponse])
async def get_ingredients(
    q: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(Ingredient).options(selectinload(Ingredient.category))
    if q:
        query = query.where(Ingredient.name.ilike(f"%{q}%"))
    query = query.order_by(Ingredient.name).limit(limit).offset(offset)
    
    result = await db.execute(query)
    ingredients = result.scalars().all()
    return ingredients

@router.get("/{id}", response_model=IngredientDetailResponse)
async def get_ingredient_detail(
    id: int,
    db: AsyncSession = Depends(get_db),
):
    query = (
        select(Ingredient)
        .options(selectinload(Ingredient.category))
        .where(Ingredient.id == id)
    )
    result = await db.execute(query)
    ingredient = result.scalar_one_or_none()
    
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
        
    return ingredient

@router.get("/{id}/pairings", response_model=list[IngredientPairingResponse])
async def get_ingredient_pairings(
    id: int,
    sort: str = Query("best", pattern="^(best|worst)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Verify ingredient exists
    ingredient = await db.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # Fetch pairings where this ingredient is either A or B
    query = (
        select(FlavorPairing)
        .options(
            selectinload(FlavorPairing.ingredient_a).selectinload(Ingredient.category),
            selectinload(FlavorPairing.ingredient_b).selectinload(Ingredient.category)
        )
        .where(
            or_(
                FlavorPairing.ingredient_a_id == id,
                FlavorPairing.ingredient_b_id == id,
            )
        )
    )
    
    if sort == "best":
        query = query.order_by(desc(FlavorPairing.affinity_score))
    else:
        query = query.order_by(asc(FlavorPairing.affinity_score))
        
    query = query.limit(limit)
    
    result = await db.execute(query)
    pairings = result.scalars().all()
    
    response = []
    for p in pairings:
        if p.ingredient_a_id == id:
            neighbor = p.ingredient_b
        else:
            neighbor = p.ingredient_a
            
        response.append(
            IngredientPairingResponse(
                neighbor_id=neighbor.id,
                neighbor_name=neighbor.name,
                neighbor_category=neighbor.category.name if neighbor.category else None,
                affinity_score=float(p.affinity_score),
                ai_rationale=p.ai_rationale,
                mechanism=p.mechanism,
            )
        )
        
    return response
