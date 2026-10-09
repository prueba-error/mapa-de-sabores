import json
from unittest.mock import AsyncMock

import httpx
import pytest
from app.config import Settings
from app.services.llm_provider import (
    GeminiProvider,
    LLMService,
    OpenAIProvider,
)


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        GEMINI_API_KEY="test_gemini_key",
        OPENAI_API_KEY="test_openai_key",
        LLM_PRIMARY_PROVIDER="gemini",
        GEMINI_MODEL="gemini-2.5-flash",
        OPENAI_MODEL="gpt-4o-mini",
        LLM_TIMEOUT_SECONDS=8.0,
    )


@pytest.mark.asyncio
async def test_gemini_provider_success():
    expected_data = {
        "sweet": 0.85,
        "sour": 0.10,
        "salty": 0.00,
        "bitter": 0.00,
        "umami": 0.05,
        "aromatic": 0.70,
    }
    gemini_api_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(expected_data)}],
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = gemini_api_response
    mock_client.post.return_value = mock_response

    provider = GeminiProvider(
        api_key="valid_key",
        model="gemini-2.5-flash",
        client=mock_client,
    )
    result = await provider.generate_json("Prompt de prueba", timeout=5.0)

    assert result == expected_data
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_openai_provider_success():
    expected_data = {
        "pairings": [
            {
                "ingredient_b": "Albahaca",
                "affinity_score": 0.95,
                "ai_rationale": "Excelente maridaje mediterráneo",
            }
        ]
    }
    openai_api_response = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(expected_data),
                }
            }
        ]
    }

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = openai_api_response
    mock_client.post.return_value = mock_response

    provider = OpenAIProvider(
        api_key="valid_key",
        model="gpt-4o-mini",
        client=mock_client,
    )
    result = await provider.generate_json("Prompt de prueba", timeout=5.0)

    assert result == expected_data
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_llm_service_fallback_to_secondary_provider(mock_settings: Settings):
    """Verifica que si Gemini falla, el servicio recurre a OpenAI dentro del presupuesto."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    # Primera llamada (Gemini) falla con ConnectError
    # Segunda llamada (OpenAI) responde exitosamente
    profile_data = {
        "sweet": 0.50,
        "sour": 0.20,
        "salty": 0.00,
        "bitter": 0.00,
        "umami": 0.10,
        "aromatic": 0.80,
    }
    openai_response = AsyncMock(spec=httpx.Response)
    openai_response.status_code = 200
    openai_response.json.return_value = {
        "choices": [{"message": {"content": json.dumps(profile_data)}}]
    }

    mock_client.post.side_effect = [
        httpx.ConnectError("Gemini no disponible"),
        openai_response,
    ]

    service = LLMService(settings=mock_settings, client=mock_client)
    profile = await service.generate_flavor_profile("Frutilla")

    assert profile.sweet == 0.50
    assert profile.aromatic == 0.80
    assert mock_client.post.await_count == 2


@pytest.mark.asyncio
async def test_llm_service_fallback_when_all_fail(mock_settings: Settings):
    """Verifica que ante falla total de ambos proveedores, se retornan fallbacks elegantes."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.TimeoutException("Timeout")

    service = LLMService(settings=mock_settings, client=mock_client)

    # 1. Fallback de perfil de sabor
    profile = await service.generate_flavor_profile("Ingrediente Desconocido")
    assert profile.sweet == 0.10
    assert profile.sour == 0.10

    # 2. Fallback de maridajes en lote -> lista vacía
    pairings = await service.evaluate_pairings_batch("Tomate", ["Albahaca", "Orégano"])
    assert pairings == []

    # 3. Fallback de explicación con rationale guardado
    explain_stored = await service.explain_pairing(
        ["Tomate", "Albahaca"],
        stored_rationale="Explicación guardada en la base de datos.",
    )
    assert explain_stored.source == "stored"
    assert explain_stored.explanation == "Explicación guardada en la base de datos."

    # 4. Fallback de explicación sin rationale guardado -> genérico
    explain_generic = await service.explain_pairing(["Ajo", "Chocolate"])
    assert explain_generic.source == "generic"

    # 5. Fallback de reemplazo -> genérico
    replacement = await service.suggest_replacement("Chocolate", ["Tomate", "Albahaca"])
    assert replacement.source == "generic"
    assert replacement.suggested_ingredient == "Hierbas aromáticas mixtas"
