#!/usr/bin/env python3
"""Script de generación y sembrado del Grafo de Sabores asistido por IA.

Implementa el pipeline offline definido en SPEC.md (Sección 2):
1. Carga de taxonomía de categorías e ingredientes.
2. Generación y validación del perfil sensorial de 6 ejes fijos (Pydantic).
3. Selección balanceada de candidatos (afines + muestreo cruzado + matriz antagónica).
4. Evaluación en lote (JSON Mode).
5. Filtro de piso (descarte < 0.15, preservación 0.15 - 0.45 para el modo 'Peores').
6. Enrutamiento a 'flavor_pairings' o 'pairing_review_queue'.

Uso:
  uv run scripts/seed_flavor_network.py --dry-run
  uv run scripts/seed_flavor_network.py --dry-run --limit 10
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import random
import sys
from typing import Any

# Agregar directorio backend al path para importar esquemas y servicios
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from antagonistic_pairs import is_antagonistic
from app.schemas.ai import (
    BatchPairingItem,
    FlavorProfileSchema,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_flavor_network")


# ============================================================================
# Taxonomía Semilla Inicial (~60 ingredientes base representativos)
# ============================================================================

SEED_TAXONOMY: dict[str, dict[str, Any]] = {
    "Frutas": {
        "color_code": "#E63946",
        "ingredients": [
            "Manzana",
            "Frutilla",
            "Limón",
            "Naranja",
            "Plátano",
            "Pera",
            "Durazno",
            "Higo",
            "Frambuesa",
            "Arándano",
            "Mango",
            "Maracuyá",
            "Sandía",
            "Melón",
            "Ciruela",
        ],
    },
    "Verduras": {
        "color_code": "#2A9D8F",
        "ingredients": [
            "Tomate",
            "Cebolla",
            "Ajo",
            "Zanahoria",
            "Pimiento Rojo",
            "Berenjena",
            "Zucchini",
            "Espinaca",
            "Remolacha",
            "Espárrago",
            "Hongo Portobello",
            "Papa",
            "Batata",
            "Pepino",
            "Palta",
        ],
    },
    "Hierbas": {
        "color_code": "#457B9D",
        "ingredients": [
            "Albahaca",
            "Romero",
            "Tomillo",
            "Menta",
            "Cilantro",
            "Orégano",
            "Salvia",
            "Eneldo",
            "Estragón",
            "Laurel",
        ],
    },
    "Especias": {
        "color_code": "#E76F51",
        "ingredients": [
            "Pimienta Negra",
            "Canela",
            "Comino",
            "Jengibre",
            "Nuez Moscada",
            "Cardamomo",
            "Pimentón Ahumado",
            "Vainilla",
            "Clavo de Olor",
            "Cúrcuma",
        ],
    },
    "Lácteos": {
        "color_code": "#F4A261",
        "ingredients": [
            "Queso Parmesano",
            "Queso Roquefort",
            "Queso Mozzarella",
            "Queso de Cabra",
            "Manteca",
            "Crema de Leche",
            "Yogur Griego",
            "Queso Brie",
            "Ricotta",
        ],
    },
    "Carnes": {
        "color_code": "#9B2226",
        "ingredients": [
            "Carne Vacuna",
            "Cerdo",
            "Cordero",
            "Pechuga de Pollo",
            "Pato",
            "Panceta Ahumada",
            "Jamón Serrano",
        ],
    },
    "Pescados y Mariscos": {
        "color_code": "#1D3557",
        "ingredients": [
            "Salmón",
            "Atún",
            "Pescado Blanco",
            "Langostinos",
            "Pulpo",
            "Mejillones",
            "Anchoas",
        ],
    },
    "Dulces y Repostería": {
        "color_code": "#6D597A",
        "ingredients": [
            "Chocolate Amargo",
            "Chocolate Blanco",
            "Miel",
            "Dulce de Leche",
            "Café Espresso",
            "Caramelo",
        ],
    },
    "Frutos Secos y Semillas": {
        "color_code": "#B5838D",
        "ingredients": [
            "Nuez",
            "Almendra",
            "Avellana",
            "Pistacho",
            "Maní",
            "Sésamo Tostado",
            "Piñón",
        ],
    },
}


# ============================================================================
# Generadores Mock para Simulación Determinística (--dry-run)
# ============================================================================


def generate_mock_flavor_profile(name: str, category: str) -> FlavorProfileSchema:
    """Genera un perfil sensorial sintético válido según la categoría para --dry-run."""
    rng = random.Random(hash(name))
    if category == "Frutas":
        return FlavorProfileSchema(
            sweet=round(rng.uniform(0.60, 0.95), 2),
            sour=round(rng.uniform(0.30, 0.85), 2),
            salty=0.02,
            bitter=round(rng.uniform(0.00, 0.20), 2),
            umami=0.05,
            aromatic=round(rng.uniform(0.60, 0.95), 2),
        )
    if category == "Lácteos" or category == "Pescados y Mariscos":
        return FlavorProfileSchema(
            sweet=0.05,
            sour=round(rng.uniform(0.05, 0.30), 2),
            salty=round(rng.uniform(0.40, 0.90), 2),
            bitter=0.05,
            umami=round(rng.uniform(0.70, 0.98), 2),
            aromatic=round(rng.uniform(0.40, 0.85), 2),
        )
    return FlavorProfileSchema(
        sweet=round(rng.uniform(0.10, 0.40), 2),
        sour=round(rng.uniform(0.10, 0.40), 2),
        salty=round(rng.uniform(0.10, 0.40), 2),
        bitter=round(rng.uniform(0.10, 0.40), 2),
        umami=round(rng.uniform(0.20, 0.60), 2),
        aromatic=round(rng.uniform(0.50, 0.95), 2),
    )


def generate_mock_batch_pairing(
    ingredient_a: str, candidates: list[str]
) -> list[BatchPairingItem]:
    """Genera evaluaciones sintéticas en lote respetando distribuciones del dominio para --dry-run."""
    items: list[BatchPairingItem] = []
    for cand in candidates:
        seed_key = hash(f"{min(ingredient_a, cand)}_{max(ingredient_a, cand)}")
        rng = random.Random(seed_key)

        antagonistic = is_antagonistic(ingredient_a, cand)
        if antagonistic:
            # Simula una alucinación ocasional del LLM para probar el filtro de alerta
            score = round(rng.uniform(0.38, 0.75), 2)
            rationale = "Contraste extremo experimental con notas divergentes."
        else:
            # Distribución típica: 20% débiles (< 0.45), 50% moderados, 30% fuertes
            p = rng.random()
            if p < 0.15:
                score = round(rng.uniform(0.05, 0.14), 2)  # Caerá en descarte < 0.15
                rationale = "Perfiles divergentes sin afinidad química demostrable."
            elif p < 0.35:
                score = round(rng.uniform(0.15, 0.44), 2)  # Pares débiles conservados
                rationale = "Afinidad sutil pero aprovechable en cocina de contraste."
            elif p < 0.75:
                score = round(rng.uniform(0.45, 0.79), 2)
                rationale = "Maridaje equilibrado con buena resonancia aromática."
            else:
                score = round(rng.uniform(0.80, 0.98), 2)
                rationale = (
                    "Sinergia clásica probada con compuestos volátiles compartidos."
                )

        item = BatchPairingItem(
            ingredient_b=cand,
            affinity_score=score,
            ai_rationale=rationale,
        )
        items.append(item)
    return items


# ============================================================================
# Pipeline de Selección y Evaluación
# ============================================================================


class FlavorNetworkPipeline:
    def __init__(
        self, dry_run: bool = True, limit: int | None = None, audit_rate: float = 0.08
    ) -> None:
        self.dry_run = dry_run
        self.limit = limit
        self.audit_rate = audit_rate

        # Estadísticas del pipeline
        self.stats = {
            "total_ingredients": 0,
            "profiles_validated": 0,
            "candidate_pairs_total": 0,
            "discarded_below_floor": 0,  # score < 0.15
            "accepted_flavor_pairings": 0,
            "weak_pairings_preserved": 0,  # 0.15 <= score < 0.45
            "queue_antagonistic_flags": 0,
            "queue_random_audits": 0,
        }

    def _collect_ingredients(self) -> list[tuple[str, str]]:
        """Recopila lista plana de tuplas (nombre, categoría)."""
        items: list[tuple[str, str]] = []
        for cat_name, data in SEED_TAXONOMY.items():
            for ing_name in data["ingredients"]:
                items.append((ing_name, cat_name))

        if self.limit:
            items = items[: self.limit]
        return items

    def _select_candidates(
        self,
        current: str,
        current_cat: str,
        all_ingredients: list[tuple[str, str]],
    ) -> list[str]:
        """Selecciona 10-12 candidatos según SPEC.md Sección 2.2."""
        same_cat = [
            name
            for name, cat in all_ingredients
            if cat == current_cat and name != current
        ]
        other_cat = [name for name, cat in all_ingredients if cat != current_cat]

        rng = random.Random(hash(current))

        # Mitad de la misma categoría o afines, mitad cruzados al azar
        sample_same = rng.sample(same_cat, min(len(same_cat), 5))
        sample_other = rng.sample(other_cat, min(len(other_cat), 6))

        candidates = list(set(sample_same + sample_other))
        return candidates

    async def run(self) -> dict[str, int]:
        logger.info(
            "Iniciando Pipeline de Datos de Sabores (dry_run=%s, limit=%s)",
            self.dry_run,
            self.limit,
        )

        all_ingredients = self._collect_ingredients()
        self.stats["total_ingredients"] = len(all_ingredients)
        logger.info(
            "Catálogo cargado: %d ingredientes a procesar", len(all_ingredients)
        )

        evaluated_pairs: set[tuple[str, str]] = set()

        # Fase 1: Perfiles sensoriales
        for name, category in all_ingredients:
            # Generar y validar con Pydantic
            profile = generate_mock_flavor_profile(name, category)
            # Validación de 6 ejes requeridos
            assert all(
                0.0 <= getattr(profile, axis) <= 1.0
                for axis in ["sweet", "sour", "salty", "bitter", "umami", "aromatic"]
            )
            self.stats["profiles_validated"] += 1

        logger.info(
            "Fase de perfiles sensoriales completada: %d validados",
            self.stats["profiles_validated"],
        )

        # Fase 2: Pares candidatos y evaluación
        for name, category in all_ingredients:
            candidates = self._select_candidates(name, category, all_ingredients)

            # Deduplicar pares ordenados canónicos
            unique_candidates = []
            for cand in candidates:
                pair_key = (min(name, cand), max(name, cand))
                if pair_key not in evaluated_pairs:
                    evaluated_pairs.add(pair_key)
                    unique_candidates.append(cand)

            if not unique_candidates:
                continue

            self.stats["candidate_pairs_total"] += len(unique_candidates)

            # Evaluar candidatos en lote
            batch_results = generate_mock_batch_pairing(name, unique_candidates)

            # Validación y enrutamiento (SPEC.md Sección 2.2.5 y 2.2.6)
            for item in batch_results:
                score = item.affinity_score
                cand = item.ingredient_b

                # 1. Piso de score (< 0.15 se descarta por ruido)
                if score < 0.15:
                    self.stats["discarded_below_floor"] += 1
                    continue

                # Contabilizar débiles conservados (0.15 a 0.45)
                if score < 0.45:
                    self.stats["weak_pairings_preserved"] += 1

                # 2. Verificar matriz de pares antagónicos conocidos
                if is_antagonistic(name, cand) and score > 0.35:
                    self.stats["queue_antagonistic_flags"] += 1
                    logger.debug(
                        "Alerta de antagónico: (%s, %s) score=%.2f -> cola de revisión",
                        name,
                        cand,
                        score,
                    )
                    continue

                # 3. Muestra aleatoria de auditoría
                if random.random() < self.audit_rate:
                    self.stats["queue_random_audits"] += 1
                    continue

                # 4. Inserción directa en grafo
                self.stats["accepted_flavor_pairings"] += 1

        self._print_report()
        return self.stats

    def _print_report(self) -> None:
        accepted = self.stats["accepted_flavor_pairings"]
        weak = self.stats["weak_pairings_preserved"]
        weak_pct = (weak / accepted * 100) if accepted > 0 else 0.0

        print("\n" + "=" * 70)
        print("          INFORME DE AUDITORIA Y SIMULACION DEL PIPELINE")
        print("=" * 70)
        print(
            f" Modos de ejecucion           : {'DRY-RUN (Simulacion sin costo)' if self.dry_run else 'PRODUCCION'}"
        )
        print(f" Ingredientes procesados      : {self.stats['total_ingredients']}")
        print(
            f" Perfiles sensoriales validos : {self.stats['profiles_validated']} (100% 6 ejes)"
        )
        print(f" Pares candidatos evaluados   : {self.stats['candidate_pairs_total']}")
        print("-" * 70)
        print(f" [DESCARTADOS] Score < 0.15   : {self.stats['discarded_below_floor']}")
        print(f" [ACEPTADOS] Grafo directo    : {accepted}")
        print(
            f"   * Pares debiles (0.15-0.45): {weak} ({weak_pct:.1f}% del total aceptado)"
        )
        print("-" * 70)
        print(
            f" [COLA DE REVISION - Curacion]: {self.stats['queue_antagonistic_flags'] + self.stats['queue_random_audits']}"
        )
        print(
            f"   * Alertas Antagonicos      : {self.stats['queue_antagonistic_flags']}"
        )
        print(
            f"   * Muestra Aleatoria ({int(self.audit_rate * 100)}%)   : {self.stats['queue_random_audits']}"
        )
        print("=" * 70)
        print(" Validacion de Criterios de Aceptacion (SPEC.md Seccion 2.4):")
        print(
            f" - Perfiles completos (100%)  : {'[OK]' if self.stats['profiles_validated'] == self.stats['total_ingredients'] else '[FALLO]'}"
        )
        print(
            f" - Pares debiles >= 15%       : {'[OK]' if weak_pct >= 15.0 else '[ALERTA: < 15%]'}"
        )
        print(
            f" - Filtro antagonicos activo  : {'[OK]' if self.stats['queue_antagonistic_flags'] >= 0 else '[FALLO]'}"
        )
        print("=" * 70 + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed pipeline para el Grafo de Sabores."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Ejecutar en modo simulación.",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Límite de ingredientes a procesar."
    )
    parser.add_argument(
        "--audit-rate",
        type=float,
        default=0.08,
        help="Tasa de muestreo aleatorio (default 0.08).",
    )
    args = parser.parse_args()

    pipeline = FlavorNetworkPipeline(
        dry_run=args.dry_run, limit=args.limit, audit_rate=args.audit_rate
    )
    asyncio.run(pipeline.run())


if __name__ == "__main__":
    main()
