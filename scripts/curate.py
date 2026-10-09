#!/usr/bin/env python3
"""CLI de Curación Editorial para la Cola de Revisión de Maridajes (pairing_review_queue).

Permite al curador gastronómico (el alumno) auditar manualmente casos dudosos
o muestras aleatorias generadas por el pipeline:
- Listar pares pendientes con motivo de alerta.
- Aprobar pares (insertándolos o actualizándolos en flavor_pairings).
- Rechazar pares incompatibles.
- Mostrar estadísticas y tasa de descarte de la auditoría aleatoria.

Uso:
  uv run scripts/curate.py --list
  uv run scripts/curate.py --approve 12
  uv run scripts/curate.py --approve 12 --score 0.75 --rationale "Afinidad corregida manualmente"
  uv run scripts/curate.py --reject 14
  uv run scripts/curate.py --stats
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.database import async_session_factory
from app.services.curation import CurationService


async def list_pending_cli(limit: int) -> None:
    async with async_session_factory() as session:
        service = CurationService(session)
        items = await service.list_pending(limit=limit)

        if not items:
            print("\n[OK] No hay pares pendientes de revisión en la cola.\n")
            return

        print("\n" + "=" * 80)
        print(f" PARES EN COLA DE REVISIÓN ({len(items)} ítems pendientes)")
        print("=" * 80)
        for it in items:
            print(f" ID #{it['id']} | [{it['flag_reason']}]")
            print(f"   Par: {it['ingredient_a_name']} (ID {it['ingredient_a_id']}) <---> {it['ingredient_b_name']} (ID {it['ingredient_b_id']})")
            print(f"   Score sugerido : {it['suggested_score']:.2f}")
            print(f"   Justificación  : {it['ai_rationale'] or 'Sin justificación'}")
            print("-" * 80)
        print()


async def approve_cli(item_id: int, score: float | None, rationale: str | None) -> None:
    async with async_session_factory() as session:
        service = CurationService(session)
        try:
            res = await service.approve(item_id, adjusted_score=score, adjusted_rationale=rationale)
            print(f"\n[APROBADO] Ítem #{res['queue_id']} aprobado con éxito.")
            print(f"   FlavorPairing ID: {res['pairing_id']} | Score: {res['score']} | Fuente: {res['source_type']}\n")
        except ValueError as err:
            print(f"\n[ERROR] {err}\n", file=sys.stderr)
            sys.exit(1)


async def reject_cli(item_id: int) -> None:
    async with async_session_factory() as session:
        service = CurationService(session)
        try:
            res = await service.reject(item_id)
            print(f"\n[RECHAZADO] Ítem #{res['queue_id']} marcado como RECHAZADO (nunca llegará al grafo público).\n")
        except ValueError as err:
            print(f"\n[ERROR] {err}\n", file=sys.stderr)
            sys.exit(1)


async def stats_cli() -> None:
    async with async_session_factory() as session:
        service = CurationService(session)
        stats = await service.get_stats()

        print("\n" + "=" * 60)
        print("     ESTADÍSTICAS DE CURACIÓN (pairing_review_queue)")
        print("=" * 60)
        print(f" Total de ítems registrados : {stats['total_items']}")
        print(f" Pendientes de revisión    : {stats['pending_review']}")
        print(f" Aprobados manualmente     : {stats['approved']}")
        print(f" Rechazados / Descartados  : {stats['rejected']}")
        print("-" * 60)
        audit = stats["random_audit"]
        print(" Muestra de Auditoría Aleatoria (random_audit):")
        print(f"   - Auditados en total    : {audit['total']}")
        print(f"   - Aprobados             : {audit['approved']}")
        print(f"   - Rechazados            : {audit['rejected']}")
        print(f"   - Tasa de rechazo / err : {audit['rejection_rate_percent']:.1f}%")
        print("=" * 60 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CLI de curación editorial para la cola de revisión de maridajes."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--list",
        action="store_true",
        help="Listar pares pendientes de revisión en la cola.",
    )
    group.add_argument(
        "--approve",
        type=int,
        metavar="ID",
        help="Aprobar un ítem por su ID de cola e insertarlo en flavor_pairings.",
    )
    group.add_argument(
        "--reject",
        type=int,
        metavar="ID",
        help="Rechazar un ítem por su ID de cola.",
    )
    group.add_argument(
        "--stats",
        action="store_true",
        help="Ver métricas de la cola y tasa de error de la muestra aleatoria.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Límite de resultados a listar (default 50).",
    )
    parser.add_argument(
        "--score",
        type=float,
        default=None,
        help="Ajustar manualmente el affinity_score al aprobar (0.00 a 1.00).",
    )
    parser.add_argument(
        "--rationale",
        type=str,
        default=None,
        help="Ajustar manualmente la justificación culinaria al aprobar.",
    )

    args = parser.parse_args()

    if args.list:
        asyncio.run(list_pending_cli(args.limit))
    elif args.approve is not None:
        asyncio.run(approve_cli(args.approve, args.score, args.rationale))
    elif args.reject is not None:
        asyncio.run(reject_cli(args.reject))
    elif args.stats:
        asyncio.run(stats_cli())


if __name__ == "__main__":
    main()
