from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.favorite import FavoriteCombination, FavoriteCombinationItem
from app.models.ingredient import Ingredient
from app.schemas.favorite import FavoriteCombinationCreate, FavoriteCombinationResponse
from app.routers.auth import get_current_user

router = APIRouter(tags=["favorites"])

@router.get("/favorites", response_model=List[FavoriteCombinationResponse])
async def get_favorites(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(FavoriteCombination)
        .where(FavoriteCombination.user_id == current_user.id)
        .options(
            selectinload(FavoriteCombination.items)
            .selectinload(FavoriteCombinationItem.ingredient)
            .selectinload(Ingredient.category)
        )
    )
    result = await db.execute(query)
    favorites = result.scalars().all()
    return favorites

@router.post("/favorites", response_model=FavoriteCombinationResponse, status_code=status.HTTP_201_CREATED)
async def create_favorite(
    favorite_in: FavoriteCombinationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ingredients exist
    query = select(Ingredient).where(Ingredient.id.in_(favorite_in.ingredient_ids))
    result = await db.execute(query)
    ingredients = result.scalars().all()
    
    if len(ingredients) != len(set(favorite_in.ingredient_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more ingredients not found"
        )
        
    # Check if this combination already exists for this user
    existing_query = select(FavoriteCombination).where(
        FavoriteCombination.user_id == current_user.id,
        FavoriteCombination.ingredient_key == favorite_in.ingredient_key
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Favorite combination already exists"
        )

    # Create the favorite
    favorite = FavoriteCombination(
        user_id=current_user.id,
        name=favorite_in.name,
        ingredient_key=favorite_in.ingredient_key
    )
    db.add(favorite)
    await db.flush() # To get the favorite.id

    # Add items
    for ing_id in favorite_in.ingredient_ids:
        item = FavoriteCombinationItem(
            combination_id=favorite.id,
            ingredient_id=ing_id
        )
        db.add(item)
        
    await db.commit()
    
    # Reload to get the relationships for response
    reload_query = (
        select(FavoriteCombination)
        .where(FavoriteCombination.id == favorite.id)
        .options(
            selectinload(FavoriteCombination.items)
            .selectinload(FavoriteCombinationItem.ingredient)
            .selectinload(Ingredient.category)
        )
    )
    reload_result = await db.execute(reload_query)
    return reload_result.scalars().first()

@router.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(FavoriteCombination).where(
        FavoriteCombination.id == favorite_id,
        FavoriteCombination.user_id == current_user.id
    )
    result = await db.execute(query)
    favorite = result.scalars().first()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
        
    await db.delete(favorite)
    await db.commit()
