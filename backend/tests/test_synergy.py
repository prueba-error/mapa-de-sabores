import pytest
from app.services.synergy import calculate_synergy


def test_synergy_n3_partial_coverage_from_spec():
    """Caso exacto de SPEC.md Sección 3.6:

    Ingredientes: [12, 45, 88] (Tomate, Albahaca, Chocolate)
    Pares conocidos:
      (12, 45): 0.94
      (12, 88): 0.12
      (45, 88): Sin dato
    """
    ingredient_ids = [12, 45, 88]
    known_pairings = {
        (12, 45): 0.94,
        (12, 88): 0.12,
    }

    result = calculate_synergy(ingredient_ids, known_pairings)

    # synergy_score = promedio(0.94, 0.12) = 0.53 * 100 = 53
    assert result.synergy_score == 53
    assert result.coverage.pairs_with_data == 2
    assert result.coverage.pairs_total == 3

    # Matriz NxN con diagonal null y celdas sin dato null
    expected_matrix = [
        [None, 0.94, 0.12],
        [0.94, None, None],
        [0.12, None, None],
    ]
    assert result.pairwise_matrix == expected_matrix

    # Ingrediente discordante: 88 tiene promedio 0.12 (< 0.45)
    assert len(result.clashing_ingredients) == 1
    assert result.clashing_ingredients[0].ingredient_id == 88
    assert result.clashing_ingredients[0].avg_affinity == 0.12


def test_synergy_n2_without_discordant():
    """Para N=2, clashing_ingredients DEBE ser siempre vacía según SPEC.md Sección 3.2."""
    ingredient_ids = [1, 2]
    known_pairings = {
        (1, 2): 0.20,  # Afinidad baja (< 0.45)
    }

    result = calculate_synergy(ingredient_ids, known_pairings)

    assert result.synergy_score == 20
    assert result.coverage.pairs_with_data == 1
    assert result.coverage.pairs_total == 1
    assert result.pairwise_matrix == [
        [None, 0.20],
        [0.20, None],
    ]
    # Regla clave: para N=2 nunca hay ingrediente discordante
    assert result.clashing_ingredients == []


def test_synergy_no_pairs_with_data():
    """Grupo donde ningún par tiene dato en la base de datos."""
    ingredient_ids = [10, 20, 30]
    known_pairings = {}

    result = calculate_synergy(ingredient_ids, known_pairings)

    assert result.synergy_score is None
    assert result.coverage.pairs_with_data == 0
    assert result.coverage.pairs_total == 3
    assert result.pairwise_matrix == [
        [None, None, None],
        [None, None, None],
        [None, None, None],
    ]
    assert result.clashing_ingredients == []


def test_synergy_n4_multiple_clashing_sorted():
    """Para N >= 3 con múltiples ingredientes discordantes, deben ordenarse de menor a mayor promedio."""
    ingredient_ids = [1, 2, 3, 4]
    # Pares:
    # 1 con 2: 0.90, 1 con 3: 0.80, 1 con 4: 0.10 -> 1 avg = (0.9+0.8+0.1)/3 = 0.60
    # 2 con 3: 0.85, 2 con 4: 0.30                -> 2 avg = (0.9+0.85+0.3)/3 = 0.683
    # 3 con 4: 0.20                               -> 3 avg = (0.8+0.85+0.2)/3 = 0.617
    # 4 avg = (0.10 + 0.30 + 0.20)/3 = 0.20 (< 0.45)
    known_pairings = {
        (1, 2): 0.90,
        (1, 3): 0.80,
        (1, 4): 0.10,
        (2, 3): 0.85,
        (2, 4): 0.30,
        (3, 4): 0.20,
    }

    result = calculate_synergy(ingredient_ids, known_pairings)

    assert result.coverage.pairs_with_data == 6
    assert result.coverage.pairs_total == 6
    # 4 es claramente discordante con promedio 0.20
    assert len(result.clashing_ingredients) == 1
    assert result.clashing_ingredients[0].ingredient_id == 4
    assert result.clashing_ingredients[0].avg_affinity == 0.20


def test_synergy_isolated_ingredient_does_not_clash():
    """Un ingrediente sin ningún par con dato no participa de la detección de discordantes."""
    ingredient_ids = [1, 2, 3]
    # Solo 1 y 2 tienen dato, 3 está aislado sin pares
    known_pairings = {
        (1, 2): 0.80,
    }

    result = calculate_synergy(ingredient_ids, known_pairings)

    assert result.synergy_score == 80
    assert result.coverage.pairs_with_data == 1
    assert result.coverage.pairs_total == 3
    # 3 no tiene pares con dato, por lo que no puede calcularse un promedio ni considerarse discordante
    assert result.clashing_ingredients == []


def test_synergy_validation_limits():
    """Valida límites de tamaño: mínimo 2, máximo 10, y no duplicados."""
    # Menos de 2 ingredientes
    with pytest.raises(ValueError, match="al menos 2"):
        calculate_synergy([1], {})

    # Más de 10 ingredientes
    with pytest.raises(ValueError, match="máximo 10"):
        calculate_synergy(list(range(1, 12)), {})

    # Duplicados
    with pytest.raises(ValueError, match="duplicados"):
        calculate_synergy([1, 2, 2], {})
