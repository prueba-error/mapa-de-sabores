import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ingredient import Ingredient
from app.models.category import Category
from app.models.pairing import FlavorPairing
from app.models.user import User

@pytest.fixture
async def sample_pairings(db_session: AsyncSession):
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Test Category Pairings {uid}", color_code="#FFFFFF")
    db_session.add(cat)
    await db_session.flush()

    ing1 = Ingredient(name=f"P Ing 1 {uid}", flavor_profile={"profile": "Test"}, category_id=cat.id)
    ing2 = Ingredient(name=f"P Ing 2 {uid}", flavor_profile={"profile": "Test"}, category_id=cat.id)
    ing3 = Ingredient(name=f"P Ing 3 {uid}", flavor_profile={"profile": "Test"}, category_id=cat.id)
    
    db_session.add_all([ing1, ing2, ing3])
    await db_session.commit()
    
    p1 = FlavorPairing(ingredient_a_id=min(ing1.id, ing2.id), ingredient_b_id=max(ing1.id, ing2.id), affinity_score=0.8)
    p2 = FlavorPairing(ingredient_a_id=min(ing2.id, ing3.id), ingredient_b_id=max(ing2.id, ing3.id), affinity_score=0.2)
    
    db_session.add_all([p1, p2])
    await db_session.commit()
    
    return [ing1, ing2, ing3]

@pytest.mark.asyncio
async def test_evaluate_pairings(client: AsyncClient, normal_user: User, normal_user_token: str, sample_pairings: list[Ingredient]):
    headers = {"Authorization": f"Bearer {normal_user_token}"}
    payload = {
        "ingredient_ids": [sample_pairings[0].id, sample_pairings[1].id, sample_pairings[2].id]
    }
    
    response = await client.post("/api/v1/pairings/evaluate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "synergy_score" in data
    assert data["synergy_score"] == 50 # (0.8 + 0.2) / 2 = 0.5 * 100
    assert data["coverage"]["pairs_with_data"] == 2
    assert data["coverage"]["pairs_total"] == 3
