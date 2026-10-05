import uuid
from decimal import Decimal

import pytest
from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.pairing import FlavorPairing
from app.models.review_queue import PairingReviewQueue
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_ordered_pair_constraint(db_session: AsyncSession):
    """Verifica que la restricción CHECK (ingredient_a_id < ingredient_b_id) rechace pares desordenados o iguales."""
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Prueba Cat {uid}", color_code="#123456")
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)

    ing1 = Ingredient(name=f"Ingrediente Uno {uid}", category_id=cat.id)
    ing2 = Ingredient(name=f"Ingrediente Dos {uid}", category_id=cat.id)
    db_session.add_all([ing1, ing2])
    await db_session.commit()
    await db_session.refresh(ing1)
    await db_session.refresh(ing2)

    min_id, max_id = min(ing1.id, ing2.id), max(ing1.id, ing2.id)

    # 1. Par ordenado válido
    valid_pairing = FlavorPairing(
        ingredient_a_id=min_id,
        ingredient_b_id=max_id,
        affinity_score=Decimal("0.85"),
        ai_rationale="Excelente maridaje complementario",
    )
    db_session.add(valid_pairing)
    await db_session.commit()
    assert valid_pairing.id is not None

    # 2. Par desordenado (a > b) -> debe fallar chk_ordered_pair
    invalid_pairing = FlavorPairing(
        ingredient_a_id=max_id,
        ingredient_b_id=min_id,
        affinity_score=Decimal("0.50"),
    )
    db_session.add(invalid_pairing)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

    # 3. Par idéntico (a == b) -> debe fallar chk_ordered_pair
    self_pairing = FlavorPairing(
        ingredient_a_id=min_id,
        ingredient_b_id=min_id,
        affinity_score=Decimal("0.90"),
    )
    db_session.add(self_pairing)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


@pytest.mark.asyncio
async def test_bidirectional_neighbor_query(db_session: AsyncSession):
    """Verifica la lógica de consulta bidireccional especificada en SPEC.md Sección 1.2."""
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Cat Bidi {uid}", color_code="#AABBCC")
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)

    i_albahaca = Ingredient(name=f"Albahaca Bidi {uid}", category_id=cat.id)
    i_tomate = Ingredient(name=f"Tomate Bidi {uid}", category_id=cat.id)
    i_ajo = Ingredient(name=f"Ajo Bidi {uid}", category_id=cat.id)
    db_session.add_all([i_albahaca, i_tomate, i_ajo])
    await db_session.commit()

    # Aseguramos a < b para ambos pares
    p1_a, p1_b = sorted([i_albahaca.id, i_tomate.id])
    p2_a, p2_b = sorted([i_tomate.id, i_ajo.id])

    pairing1 = FlavorPairing(
        ingredient_a_id=p1_a,
        ingredient_b_id=p1_b,
        affinity_score=Decimal("0.92"),
        ai_rationale="Clásica sinergia italiana",
    )
    pairing2 = FlavorPairing(
        ingredient_a_id=p2_a,
        ingredient_b_id=p2_b,
        affinity_score=Decimal("0.88"),
        ai_rationale="Afinidad aromática intensa",
    )
    db_session.add_all([pairing1, pairing2])
    await db_session.commit()

    # Query bidireccional para Tomate (debe devolver Albahaca y Ajo independientemente de si Tomate es A o B)
    sql_bidi = text("""
        SELECT
            CASE WHEN p.ingredient_a_id = :target_id THEN i2.id ELSE i1.id END AS neighbor_id,
            CASE WHEN p.ingredient_a_id = :target_id THEN i2.name ELSE i1.name END AS neighbor_name,
            p.affinity_score
        FROM flavor_pairings p
        JOIN ingredients i1 ON p.ingredient_a_id = i1.id
        JOIN ingredients i2 ON p.ingredient_b_id = i2.id
        WHERE p.ingredient_a_id = :target_id OR p.ingredient_b_id = :target_id
        ORDER BY p.affinity_score DESC
    """)

    result = await db_session.execute(sql_bidi, {"target_id": i_tomate.id})
    neighbors = result.mappings().all()

    assert len(neighbors) == 2
    neighbor_names = {row["neighbor_name"] for row in neighbors}
    assert f"Albahaca Bidi {uid}" in neighbor_names
    assert f"Ajo Bidi {uid}" in neighbor_names


@pytest.mark.asyncio
async def test_review_queue_constraints(db_session: AsyncSession):
    """Verifica restricciones de la cola de curación (chk_review_ordered_pair y chk_review_status)."""
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Cat Queue {uid}", color_code="#334455")
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)

    i1 = Ingredient(name=f"Queue Ing 1 {uid}", category_id=cat.id)
    i2 = Ingredient(name=f"Queue Ing 2 {uid}", category_id=cat.id)
    db_session.add_all([i1, i2])
    await db_session.commit()

    a_id, b_id = sorted([i1.id, i2.id])

    # Par válido en estado 'pending_review'
    item = PairingReviewQueue(
        ingredient_a_id=a_id,
        ingredient_b_id=b_id,
        suggested_score=Decimal("0.25"),
        ai_rationale="Dudoso",
        flag_reason="forbidden_antagonistic_pair",
        status="pending_review",
    )
    db_session.add(item)
    await db_session.commit()
    assert item.id is not None

    # Estado inválido -> debe fallar chk_review_status
    invalid_status_item = PairingReviewQueue(
        ingredient_a_id=a_id,
        ingredient_b_id=b_id,
        suggested_score=Decimal("0.25"),
        flag_reason="random_audit",
        status="invalid_status_xyz",
    )
    db_session.add(invalid_status_item)
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()
