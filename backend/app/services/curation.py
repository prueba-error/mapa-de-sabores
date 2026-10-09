"""Servicio de Curación de Pares (Pairing Review Queue).

Implementa la lógica de negocio para la gestión editorial y auditoría
de la cola de revisión de pares dudosos o auditados:
- Listado de pares pendientes con nombres de ingredientes y motivos de alerta.
- Aprobación de pares: marca como 'approved' e inserta/actualiza en flavor_pairings
  con source_type = 'manual_review'.
- Rechazo de pares: marca como 'rejected' (nunca entra al grafo público).
- Estadísticas globales y tasa de error de la muestra aleatoria (random_audit).

(SPEC.md Sección 2.2.7 y 3.5).
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient
from app.models.pairing import FlavorPairing
from app.models.review_queue import PairingReviewQueue


class CurationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_pending(self, limit: int = 50) -> list[dict[str, Any]]:
        """Devuelve los ítems en 'pending_review' ordenados por fecha de creación ascendente."""
        stmt = (
            select(PairingReviewQueue)
            .where(PairingReviewQueue.status == "pending_review")
            .order_by(PairingReviewQueue.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        output: list[dict[str, Any]] = []
        for item in items:
            ing_a = await self.session.get(Ingredient, item.ingredient_a_id)
            ing_b = await self.session.get(Ingredient, item.ingredient_b_id)
            output.append({
                "id": item.id,
                "ingredient_a_id": item.ingredient_a_id,
                "ingredient_a_name": ing_a.name if ing_a else f"ID {item.ingredient_a_id}",
                "ingredient_b_id": item.ingredient_b_id,
                "ingredient_b_name": ing_b.name if ing_b else f"ID {item.ingredient_b_id}",
                "suggested_score": float(item.suggested_score),
                "ai_rationale": item.ai_rationale,
                "flag_reason": item.flag_reason,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            })
        return output

    async def approve(
        self,
        item_id: int,
        adjusted_score: float | None = None,
        adjusted_rationale: str | None = None,
    ) -> dict[str, Any]:
        """Aprueba un ítem de la cola, moviéndolo a flavor_pairings con source_type='manual_review'."""
        item = await self.session.get(PairingReviewQueue, item_id)
        if not item:
            raise ValueError(f"No se encontró el ítem con id {item_id} en la cola de revisión.")

        if item.status != "pending_review":
            raise ValueError(f"El ítem {item_id} ya fue procesado con estado '{item.status}'.")

        final_score = (
            Decimal(str(adjusted_score)) if adjusted_score is not None else item.suggested_score
        )
        final_rationale = adjusted_rationale if adjusted_rationale is not None else item.ai_rationale

        # Actualizar estado en la cola
        now = datetime.now(UTC)
        item.status = "approved"
        item.reviewed_at = now

        # Verificar si ya existe en flavor_pairings para actualizar o insertar
        stmt = select(FlavorPairing).where(
            FlavorPairing.ingredient_a_id == item.ingredient_a_id,
            FlavorPairing.ingredient_b_id == item.ingredient_b_id,
        )
        res = await self.session.execute(stmt)
        existing_pairing = res.scalar_one_or_none()

        if existing_pairing:
            existing_pairing.affinity_score = final_score
            existing_pairing.ai_rationale = final_rationale
            existing_pairing.source_type = "manual_review"
            pairing_id = existing_pairing.id
        else:
            new_pairing = FlavorPairing(
                ingredient_a_id=item.ingredient_a_id,
                ingredient_b_id=item.ingredient_b_id,
                affinity_score=final_score,
                ai_rationale=final_rationale,
                source_type="manual_review",
            )
            self.session.add(new_pairing)
            await self.session.flush()
            pairing_id = new_pairing.id

        await self.session.commit()
        return {
            "queue_id": item.id,
            "pairing_id": pairing_id,
            "status": "approved",
            "score": float(final_score),
            "source_type": "manual_review",
        }

    async def reject(self, item_id: int) -> dict[str, Any]:
        """Rechaza un ítem de la cola marcándolo como 'rejected'."""
        item = await self.session.get(PairingReviewQueue, item_id)
        if not item:
            raise ValueError(f"No se encontró el ítem con id {item_id} en la cola de revisión.")

        if item.status != "pending_review":
            raise ValueError(f"El ítem {item_id} ya fue procesado con estado '{item.status}'.")

        now = datetime.now(UTC)
        item.status = "rejected"
        item.reviewed_at = now

        await self.session.commit()
        return {
            "queue_id": item.id,
            "status": "rejected",
            "reviewed_at": now.isoformat(),
        }

    async def get_stats(self) -> dict[str, Any]:
        """Calcula estadísticas generales de la cola y tasa de error de la auditoría aleatoria."""
        # Totales por estado
        status_stmt = select(
            PairingReviewQueue.status, func.count(PairingReviewQueue.id)
        ).group_by(PairingReviewQueue.status)
        status_res = await self.session.execute(status_stmt)
        status_counts = dict(status_res.all())

        pending = status_counts.get("pending_review", 0)
        approved = status_counts.get("approved", 0)
        rejected = status_counts.get("rejected", 0)
        total = pending + approved + rejected

        # Desglose específico para 'random_audit'
        audit_stmt = (
            select(PairingReviewQueue.status, func.count(PairingReviewQueue.id))
            .where(PairingReviewQueue.flag_reason == "random_audit")
            .group_by(PairingReviewQueue.status)
        )
        audit_res = await self.session.execute(audit_stmt)
        audit_counts = dict(audit_res.all())

        audit_approved = audit_counts.get("approved", 0)
        audit_rejected = audit_counts.get("rejected", 0)
        audit_reviewed = audit_approved + audit_rejected
        rejection_rate = (
            round((audit_rejected / audit_reviewed) * 100, 2) if audit_reviewed > 0 else 0.0
        )

        return {
            "total_items": total,
            "pending_review": pending,
            "approved": approved,
            "rejected": rejected,
            "random_audit": {
                "total": sum(audit_counts.values()),
                "approved": audit_approved,
                "rejected": audit_rejected,
                "rejection_rate_percent": rejection_rate,
            },
        }
