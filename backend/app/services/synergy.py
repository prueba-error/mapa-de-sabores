"""Servicio de cálculo determinístico de sinergia NxN."""

from app.schemas.synergy import (
    ClashingIngredient,
    CoverageInfo,
    SynergyEvaluationResponse,
)


def calculate_synergy(
    ingredient_ids: list[int],
    known_pairings: dict[tuple[int, int], float],
) -> SynergyEvaluationResponse:
    """Evalúa la sinergia determinística de un grupo de 2 a 10 ingredientes.

    Parámetros:
      ingredient_ids: Lista ordenada de identificadores de ingredientes seleccionados.
      known_pairings: Diccionario con afinidades conocidas con claves canónicas (a, b) con a < b.

    Reglas de negocio (SPEC.md Sección 3.2):
      - synergy_score: promedio simple de los pares con dato escalado a porcentaje (0-100);
        None si no hay pares con dato.
      - coverage: pares_con_dato sobre el total combinatorio N*(N-1)/2.
      - pairwise_matrix: matriz simétrica NxN con None en diagonal y celdas sin dato.
      - clashing_ingredients: solo para N >= 3; ingredientes con afinidad promedio < 0.45
        frente al resto del grupo con dato. Lista vacía para N = 2.
    """
    n = len(ingredient_ids)
    if n < 2:
        raise ValueError("Se requieren al menos 2 ingredientes para evaluar sinergia.")
    if n > 10:
        raise ValueError(
            "Se admiten como máximo 10 ingredientes para evaluar sinergia."
        )
    if len(set(ingredient_ids)) != n:
        raise ValueError("La lista de ingredientes contiene duplicados.")

    pairs_total = n * (n - 1) // 2
    pairwise_matrix: list[list[float | None]] = [[None] * n for _ in range(n)]

    scores_with_data: list[float] = []
    ingredient_stats: dict[int, dict[str, float]] = {
        ing_id: {"sum": 0.0, "count": 0.0} for ing_id in ingredient_ids
    }

    for i in range(n):
        for j in range(i + 1, n):
            id_a = ingredient_ids[i]
            id_b = ingredient_ids[j]
            canonical_key = (min(id_a, id_b), max(id_a, id_b))

            if (
                canonical_key in known_pairings
                and known_pairings[canonical_key] is not None
            ):
                score = round(float(known_pairings[canonical_key]), 2)
                pairwise_matrix[i][j] = score
                pairwise_matrix[j][i] = score
                scores_with_data.append(score)

                ingredient_stats[id_a]["sum"] += score
                ingredient_stats[id_a]["count"] += 1.0
                ingredient_stats[id_b]["sum"] += score
                ingredient_stats[id_b]["count"] += 1.0

    synergy_score: int | None = None
    if scores_with_data:
        synergy_score = round((sum(scores_with_data) / len(scores_with_data)) * 100)

    clashing_ingredients: list[ClashingIngredient] = []
    if n >= 3:
        for ing_id in ingredient_ids:
            st = ingredient_stats[ing_id]
            if st["count"] > 0:
                avg = round(st["sum"] / st["count"], 2)
                if avg < 0.45:
                    clashing_ingredients.append(
                        ClashingIngredient(ingredient_id=ing_id, avg_affinity=avg)
                    )
        # Ordenar ascendente por avg_affinity: el de menor afinidad es el discordante principal
        clashing_ingredients.sort(key=lambda item: item.avg_affinity)

    return SynergyEvaluationResponse(
        synergy_score=synergy_score,
        coverage=CoverageInfo(
            pairs_with_data=len(scores_with_data),
            pairs_total=pairs_total,
        ),
        pairwise_matrix=pairwise_matrix,
        clashing_ingredients=clashing_ingredients,
    )
