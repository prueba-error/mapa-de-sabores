"""Servicio agnóstico de integración con Modelos de Lenguaje (LLM).

Soporta adaptadores para Google Gemini y OpenAI con presupuesto estricto
de tiempo total (8.0s), reintentos, conmutación por error (fallback) y
respuestas garantizadas mediante JSON Mode y Pydantic.
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import Settings, get_settings
from app.schemas.ai import (
    AIExplanationResponse,
    AIReplacementResponse,
    BatchPairingItem,
    BatchPairingResponse,
    FlavorProfileSchema,
)

logger = logging.getLogger("mapa_sabores.llm")

LLM_OPERATIONAL_ERRORS = (
    httpx.HTTPError,
    ValueError,
    KeyError,
    json.JSONDecodeError,
    RuntimeError,
    TimeoutError,
    ValidationError,
)


# ============================================================================
# Prompts del Dominio (SPEC.md Sección 2.3)
# ============================================================================

SYSTEM_PROMPT_CHEF = (
    "Eres un chef ejecutivo y científico gastronómico experto en maridajes moleculares. "
    "Tu tarea es analizar y evaluar combinaciones de ingredientes basándote en afinidad química, "
    "contrastes organolépticos y tradiciones culinarias consolidadas. "
    "Responde estricta y únicamente con un objeto JSON válido según el esquema solicitado."
)

PROMPT_FLAVOR_PROFILE = """
Analiza el ingrediente '{ingredient_name}'{desc_clause}.
Determina la intensidad de sus seis ejes sensoriales en una escala de 0.00 a 1.00:
- sweet: dulzura
- sour: acidez
- salty: salinidad
- bitter: amargor
- umami: sabrosidad umami
- aromatic: intensidad y complejidad de compuestos volátiles

Responde con un JSON en este formato exacto:
{{
  "sweet": 0.00,
  "sour": 0.00,
  "salty": 0.00,
  "bitter": 0.00,
  "umami": 0.00,
  "aromatic": 0.00
}}
"""

PROMPT_BATCH_PAIRING = """
Evalúa la afinidad organoléptica entre el ingrediente base '{ingredient_a}' y cada uno de los siguientes candidatos:
{candidates_list}

Para cada candidato, genera:
- affinity_score: número entre 0.00 y 1.00 que refleje qué tan bien maridan.
- ai_rationale: explicación concisa y técnica del maridaje en español (máximo 250 caracteres).

Responde con un JSON en este formato exacto:
{{
  "pairings": [
    {{
      "ingredient_b": "Nombre del Candidato",
      "affinity_score": 0.85,
      "ai_rationale": "Notas complementarias de..."
    }}
  ]
}}
"""

PROMPT_EXPLAIN_PAIRING = """
Explica en prosa culinaria por qué maridan los siguientes ingredientes:
{ingredients_list}

La explicación debe ser atractiva, técnica pero accesible, en español, de 2 a 3 oraciones (máximo 280 caracteres).
Responde con un JSON:
{{
  "explanation": "Texto de la explicación..."
}}
"""

PROMPT_SUGGEST_REPLACEMENT = """
En una combinación que incluye {other_ingredients}, el ingrediente '{target_ingredient}' resulta discordante o incompatible.
Sugiere un ingrediente de reemplazo que armonice mejor con el conjunto.

Responde con un JSON:
{{
  "suggested_ingredient": "Nombre del ingrediente sugerido",
  "rationale": "Justificación culinaria concisa (máximo 250 caracteres)"
}}
"""


# ============================================================================
# Interfaz Abstracta de Proveedor
# ============================================================================


class BaseLLMProvider(ABC):
    """Interfaz base para proveedores de LLM."""

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        timeout: float,
        system_prompt: str = SYSTEM_PROMPT_CHEF,
    ) -> dict[str, Any]:
        """Envía un prompt y obtiene un diccionario decodificado desde la respuesta JSON."""


# ============================================================================
# Adaptador Google Gemini
# ============================================================================


class GeminiProvider(BaseLLMProvider):
    """Adaptador para Google Gemini API usando JSON Mode."""

    def __init__(self, api_key: str, model: str, client: httpx.AsyncClient) -> None:
        self.api_key = api_key
        self.model = model
        self.client = client
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_json(
        self,
        prompt: str,
        timeout: float,
        system_prompt: str = SYSTEM_PROMPT_CHEF,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY no configurada.")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"{system_prompt}\n\n{prompt}"}],
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }

        response = await self.client.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        try:
            candidates = data.get("candidates", [])
            text_part = candidates[0]["content"]["parts"][0]["text"]
            return json.loads(text_part)  # type: ignore[no-any-return]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Respuesta inválida de Gemini: {e}") from e


# ============================================================================
# Adaptador OpenAI
# ============================================================================


class OpenAIProvider(BaseLLMProvider):
    """Adaptador para OpenAI API usando JSON Mode."""

    def __init__(self, api_key: str, model: str, client: httpx.AsyncClient) -> None:
        self.api_key = api_key
        self.model = model
        self.client = client
        self.url = "https://api.openai.com/v1/chat/completions"

    async def generate_json(
        self,
        prompt: str,
        timeout: float,
        system_prompt: str = SYSTEM_PROMPT_CHEF,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no configurada.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        response = await self.client.post(
            self.url, headers=headers, json=payload, timeout=timeout
        )
        response.raise_for_status()
        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)  # type: ignore[no-any-return]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Respuesta inválida de OpenAI: {e}") from e


# ============================================================================
# Orquestador con Presupuesto Total de 8s y Fallback
# ============================================================================


class LLMService:
    """Orquestador agnóstico de servicios de IA.

    Garantiza:
    1. Presupuesto estricto de tiempo total (default: 8.0 s).
    2. Conmutación automática a proveedor secundario en caso de error o agotamiento parcial.
    3. Validación estricta con Pydantic.
    4. Fallbacks determinísticos elegantes ante indisponibilidad de API externa.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._external_client = client
        self._internal_client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._external_client is not None:
            return self._external_client
        if self._internal_client is None:
            self._internal_client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.settings.LLM_TIMEOUT_SECONDS),
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
            )
        return self._internal_client

    async def close(self) -> None:
        if self._internal_client is not None:
            await self._internal_client.aclose()
            self._internal_client = None

    def _get_providers(self) -> list[BaseLLMProvider]:
        """Devuelve los proveedores ordenados por preferencia primaria y secundaria."""
        client = self._get_client()
        gemini = GeminiProvider(
            api_key=self.settings.GEMINI_API_KEY,
            model=self.settings.GEMINI_MODEL,
            client=client,
        )
        openai = OpenAIProvider(
            api_key=self.settings.OPENAI_API_KEY,
            model=self.settings.OPENAI_MODEL,
            client=client,
        )

        if self.settings.LLM_PRIMARY_PROVIDER.lower() == "openai":
            return [openai, gemini]
        return [gemini, openai]

    async def _execute_with_budget(self, prompt: str) -> dict[str, Any]:
        """Ejecuta la llamada probando proveedores dentro del presupuesto de tiempo restante."""
        total_budget = self.settings.LLM_TIMEOUT_SECONDS
        start_time = time.monotonic()
        providers = self._get_providers()

        for idx, provider in enumerate(providers):
            elapsed = time.monotonic() - start_time
            remaining_time = total_budget - elapsed
            if remaining_time <= 0.5:
                logger.warning("Presupuesto de tiempo agotado para llamadas LLM.")
                break

            # Asignar tiempo restante al intento actual
            try:
                logger.info(
                    "Consultando proveedor LLM (%s) con presupuesto restante %.2fs",
                    type(provider).__name__,
                    remaining_time,
                )
                return await provider.generate_json(prompt, timeout=remaining_time)
            except LLM_OPERATIONAL_ERRORS as exc:
                logger.warning(
                    "Fallo en proveedor %s: %s. Intentando siguiente si está disponible...",
                    type(provider).__name__,
                    exc,
                )
                continue

        raise RuntimeError(
            "Todos los proveedores LLM fallaron o se agotó el presupuesto de tiempo."
        )

    # ------------------------------------------------------------------------
    # Casos de Uso del Dominio
    # ------------------------------------------------------------------------

    async def generate_flavor_profile(
        self,
        ingredient_name: str,
        description: str | None = None,
    ) -> FlavorProfileSchema:
        """Genera el perfil sensorial de 6 ejes fijos para un ingrediente."""
        desc_clause = f" ({description})" if description else ""
        prompt = PROMPT_FLAVOR_PROFILE.format(
            ingredient_name=ingredient_name,
            desc_clause=desc_clause,
        )

        try:
            data = await self._execute_with_budget(prompt)
            return FlavorProfileSchema.model_validate(data)
        except LLM_OPERATIONAL_ERRORS as exc:
            logger.error(
                "Error generando perfil de sabor para '%s': %s", ingredient_name, exc
            )
            # Fallback seguro con perfil equilibrado neutral
            return FlavorProfileSchema(
                sweet=0.10,
                sour=0.10,
                salty=0.10,
                bitter=0.10,
                umami=0.10,
                aromatic=0.30,
            )

    async def evaluate_pairings_batch(
        self,
        ingredient_a: str,
        candidates: list[str],
    ) -> list[BatchPairingItem]:
        """Evalúa un lote de candidatos contra un ingrediente base."""
        if not candidates:
            return []

        candidates_text = "\n".join(f"- {c}" for c in candidates)
        prompt = PROMPT_BATCH_PAIRING.format(
            ingredient_a=ingredient_a,
            candidates_list=candidates_text,
        )

        try:
            data = await self._execute_with_budget(prompt)
            response = BatchPairingResponse.model_validate(data)
            return response.pairings
        except LLM_OPERATIONAL_ERRORS as exc:
            logger.error(
                "Error evaluando lote de maridajes para '%s': %s", ingredient_a, exc
            )
            return []

    async def explain_pairing(
        self,
        ingredient_names: list[str],
        stored_rationale: str | None = None,
    ) -> AIExplanationResponse:
        """Genera una explicación organoléptica con fallback a guardada o genérica."""
        if len(ingredient_names) < 2:
            return AIExplanationResponse(
                explanation="Se requieren al menos dos ingredientes para explicar una combinación.",
                source="generic",
            )

        # Si tenemos stored_rationale y fallan los LLM, este será el primer fallback
        prompt = PROMPT_EXPLAIN_PAIRING.format(
            ingredients_list=", ".join(ingredient_names),
        )

        try:
            data = await self._execute_with_budget(prompt)
            explanation = data.get("explanation", "").strip()
            if explanation:
                return AIExplanationResponse(explanation=explanation, source="llm")
        except LLM_OPERATIONAL_ERRORS as exc:
            logger.warning("No se pudo obtener explicación LLM: %s", exc)

        if stored_rationale:
            return AIExplanationResponse(explanation=stored_rationale, source="stored")

        return AIExplanationResponse(
            explanation=(
                f"La combinación de {', '.join(ingredient_names)} presenta afinidades sensoriales "
                "que interactúan creando contrastes gastronómicos interesantes."
            ),
            source="generic",
        )

    async def suggest_replacement(
        self,
        target_ingredient: str,
        other_ingredients: list[str],
    ) -> AIReplacementResponse:
        """Sugiere un reemplazo para el ingrediente discordante."""
        prompt = PROMPT_SUGGEST_REPLACEMENT.format(
            target_ingredient=target_ingredient,
            other_ingredients=", ".join(other_ingredients),
        )

        try:
            data = await self._execute_with_budget(prompt)
            suggested = data.get("suggested_ingredient", "").strip()
            rationale = data.get("rationale", "").strip()
            if suggested and rationale:
                return AIReplacementResponse(
                    suggested_ingredient=suggested,
                    rationale=rationale,
                    source="llm",
                )
        except LLM_OPERATIONAL_ERRORS as exc:
            logger.warning("No se pudo obtener reemplazo LLM: %s", exc)

        return AIReplacementResponse(
            suggested_ingredient="Hierbas aromáticas mixtas",
            rationale="Aporte aromático neutro y versátil para balancear el perfil global del plato.",
            source="generic",
        )
