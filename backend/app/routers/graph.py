from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.pairing import FlavorPairing
from app.models.ingredient import Ingredient
from app.schemas.graph import GraphResponse, GraphNode, GraphEdge

router = APIRouter(prefix="/graph", tags=["Graph"])

@router.get("", response_model=GraphResponse)
async def get_graph(
    sort: str = Query("best", pattern="^(best|worst|all)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_affinity: float | None = Query(None, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db),
):
    # Set default min_affinity based on sort mode if not provided
    if min_affinity is None:
        if sort == "best":
            min_affinity = 0.50
        else:
            min_affinity = 0.00
            
    query = (
        select(FlavorPairing)
        .options(
            selectinload(FlavorPairing.ingredient_a).selectinload(Ingredient.category),
            selectinload(FlavorPairing.ingredient_b).selectinload(Ingredient.category)
        )
        .where(FlavorPairing.affinity_score >= min_affinity)
    )
    
    if sort == "best":
        query = query.order_by(desc(FlavorPairing.affinity_score))
    elif sort == "worst":
        query = query.order_by(asc(FlavorPairing.affinity_score))
    # if "all", we don't apply specific sorting or could sort by id
    
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    pairings = result.scalars().all()
    
    nodes_map = {}
    edges = []
    
    for p in pairings:
        for ing in (p.ingredient_a, p.ingredient_b):
            if ing.id not in nodes_map:
                nodes_map[ing.id] = GraphNode(
                    id=ing.id,
                    name=ing.name,
                    category=ing.category.name if ing.category else "Sin Categoría",
                    color_code=ing.category.color_code if ing.category else "#cccccc"
                )
        
        edges.append(
            GraphEdge(
                ingredient_a_id=p.ingredient_a_id,
                ingredient_b_id=p.ingredient_b_id,
                affinity_score=float(p.affinity_score),
                mechanism=p.mechanism
            )
        )
        
    return GraphResponse(
        nodes=list(nodes_map.values()),
        edges=edges
    )
