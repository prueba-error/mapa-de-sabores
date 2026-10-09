import uuid
from decimal import Decimal

import pytest
from app.models.category import Category
from app.models.ingredient import Ingredient
from app.models.pairing import FlavorPairing
from app.models.review_queue import PairingReviewQueue
from app.services.curation import CurationService
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_curation_service_full_workflow(db_session: AsyncSession):
    """Verifica el flujo completo de CurationService: list, approve, reject y stats."""
    uid = uuid.uuid4().hex[:6]
    cat = Category(name=f"Cat Curate {uid}", color_code="#112233")
    db_session.add(cat)
    await db_session.commit()
    await db_session.refresh(cat)

    i1 = Ingredient(name=f"Ing Curate 1 {uid}", category_id=cat.id)
    i2 = Ingredient(name=f"Ing Curate 2 {uid}", category_id=cat.id)
    i3 = Ingredient(name=f"Ing Curate 3 {uid}", category_id=cat.id)
    db_session.add_all([i1, i2, i3])
    await db_session.commit()

    a_id, b_id = sorted([i1.id, i2.id])
    b2_id, c_id = sorted([i2.id, i3.id])

    # 1. Crear dos ítems en la cola (uno antagónico y uno de auditoría aleatoria)
    item_antag = PairingReviewQueue(
        ingredient_a_id=a_id,
        ingredient_b_id=b_id,
        suggested_score=Decimal("0.42"),
        ai_rationale="Alerta de incompatibilidad",
        flag_reason="forbidden_antagonistic_pair",
        status="pending_review",
    )
    item_audit = PairingReviewQueue(
        ingredient_a_id=b2_id,
        ingredient_b_id=c_id,
        suggested_score=Decimal("0.85"),
        ai_rationale="Maridaje armónico evaluado",
        flag_reason="random_audit",
        status="pending_review",
    )
    db_session.add_all([item_antag, item_audit])
    await db_session.commit()

    service = CurationService(db_session)

    # 2. Listar pendientes
    pending = await service.list_pending()
    pending_ids = [p["id"] for p in pending]
    assert item_antag.id in pending_ids
    assert item_audit.id in pending_ids

    # 3. Rechazar el par antagónico
    rej_res = await service.reject(item_antag.id)
    assert rej_res["status"] == "rejected"
    await db_session.refresh(item_antag)
    assert item_antag.status == "rejected"
    assert item_antag.reviewed_at is not None

    # 4. Aprobar el par de auditoría con ajuste manual opcional
    app_res = await service.approve(
        item_audit.id, adjusted_score=0.90, adjusted_rationale="Aprobado por el chef"
    )
    assert app_res["status"] == "approved"
    assert app_res["score"] == 0.90
    assert app_res["source_type"] == "manual_review"

    # Verificar que se insertó en flavor_pairings
    pairing = await db_session.get(FlavorPairing, app_res["pairing_id"])
    assert pairing is not None
    assert pairing.ingredient_a_id == b2_id
    assert pairing.ingredient_b_id == c_id
    assert pairing.affinity_score == Decimal("0.90")
    assert pairing.ai_rationale == "Aprobado por el chef"
    assert pairing.source_type == "manual_review"

    # 5. Intentar re-aprobar o re-rechazar debe fallar
    with pytest.raises(ValueError, match="ya fue procesado"):
        await service.approve(item_audit.id)

    with pytest.raises(ValueError, match="ya fue procesado"):
        await service.reject(item_antag.id)

    # 6. Estadísticas
    stats = await service.get_stats()
    assert stats["approved"] >= 1
    assert stats["rejected"] >= 1
    assert stats["random_audit"]["approved"] >= 1
