import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.category import Category
from app.models.favorite import FavoriteCombination, FavoriteCombinationItem

@pytest.fixture
async def sample_ingredients(db_session: AsyncSession):
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Test Category {uid}", color_code="#FFFFFF")
    db_session.add(cat)
    await db_session.flush()

    ing1 = Ingredient(name=f"Ing 1 {uid}", flavor_profile={"profile": "Test"}, category_id=cat.id)
    ing2 = Ingredient(name=f"Ing 2 {uid}", flavor_profile={"profile": "Test"}, category_id=cat.id)
    
    db_session.add_all([ing1, ing2])
    await db_session.commit()
    
    return [ing1, ing2]

@pytest.mark.asyncio
async def test_create_favorite(client: AsyncClient, normal_user: User, normal_user_token: str, sample_ingredients: list[Ingredient]):
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    payload = {
        "name": "My Favorite",
        "ingredient_key": f"{sample_ingredients[0].id},{sample_ingredients[1].id}",
        "ingredient_ids": [sample_ingredients[0].id, sample_ingredients[1].id]
    }
    
    response = await client.post("/api/v1/favorites", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Favorite"
    assert data["ingredient_key"] == payload["ingredient_key"]
    assert len(data["items"]) == 2

@pytest.mark.asyncio
async def test_get_favorites(client: AsyncClient, normal_user: User, normal_user_token: str, db_session: AsyncSession, sample_ingredients: list[Ingredient]):
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    # Create favorite
    fav = FavoriteCombination(user_id=normal_user.id, name="Test", ingredient_key=f"fav_{uuid.uuid4().hex[:6]}")
    db_session.add(fav)
    await db_session.flush()
    db_session.add(FavoriteCombinationItem(combination_id=fav.id, ingredient_id=sample_ingredients[0].id))
    db_session.add(FavoriteCombinationItem(combination_id=fav.id, ingredient_id=sample_ingredients[1].id))
    await db_session.commit()

    response = await client.get("/api/v1/favorites", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    names = [d["name"] for d in data]
    assert "Test" in names

@pytest.mark.asyncio
async def test_delete_favorite(client: AsyncClient, normal_user: User, normal_user_token: str, db_session: AsyncSession, sample_ingredients: list[Ingredient]):
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    
    fav = FavoriteCombination(user_id=normal_user.id, name="Test", ingredient_key=f"fav_{uuid.uuid4().hex[:6]}")
    db_session.add(fav)
    await db_session.commit()
    
    response = await client.delete(f"/api/v1/favorites/{fav.id}", headers=headers)
    assert response.status_code == 204
    
    response = await client.get("/api/v1/favorites", headers=headers)
    assert response.status_code == 200
    # Make sure deleted favorite is not there
    ids = [d["id"] for d in response.json()]
    assert fav.id not in ids
