import pytest

from scripts.antagonistic_pairs import is_antagonistic
from scripts.seed_flavor_network import FlavorNetworkPipeline


def test_antagonistic_pairs_detection():
    # Pares antagónicos conocidos
    assert is_antagonistic("Pescado Blanco", "Dulce de Leche") is True
    assert (
        is_antagonistic("dulce de leche", "pescado blanco") is True
    )  # insensibilidad a mayúsculas
    assert is_antagonistic("Sandía", "Ajo") is True
    assert is_antagonistic("Chocolate", "Atún") is True

    # Pares armoniosos o normales
    assert is_antagonistic("Tomate", "Albahaca") is False
    assert is_antagonistic("Frutilla", "Crema") is False


@pytest.mark.asyncio
async def test_seed_pipeline_dry_run_execution():
    """Ejecuta el pipeline con --dry-run y verifica que se cumplan las métricas de SPEC.md."""
    pipeline = FlavorNetworkPipeline(dry_run=True, limit=15)
    stats = await pipeline.run()

    # 1. Todos los ingredientes procesados tienen perfil validado
    assert stats["total_ingredients"] == 15
    assert stats["profiles_validated"] == 15

    # 2. Se evaluaron pares candidatos
    assert stats["candidate_pairs_total"] > 0

    # 3. Se clasificaron pares aceptados y descartados
    assert stats["accepted_flavor_pairings"] > 0
    assert stats["discarded_below_floor"] >= 0

    # 4. Los pares débiles conservados representan al menos 15% del total aceptado
    weak_pct = (
        stats["weak_pairings_preserved"] / stats["accepted_flavor_pairings"]
    ) * 100
    assert weak_pct >= 15.0
