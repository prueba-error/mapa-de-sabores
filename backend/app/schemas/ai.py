"""Esquemas Pydantic para servicios de IA, perfiles sensoriales y evaluación en lote."""

from typing import Literal

from pydantic import BaseModel, Field


class FlavorProfileSchema(BaseModel):
    """Perfil sensorial de 6 ejes fijos normalizados entre 0.00 y 1.00."""

    sweet: float = Field(ge=0.0, le=1.0, description="Dulzura (0.00 - 1.00)")
    sour: float = Field(ge=0.0, le=1.0, description="Acidez (0.00 - 1.00)")
    salty: float = Field(ge=0.0, le=1.0, description="Salinidad (0.00 - 1.00)")
    bitter: float = Field(ge=0.0, le=1.0, description="Amargor (0.00 - 1.00)")
    umami: float = Field(ge=0.0, le=1.0, description="Umami (0.00 - 1.00)")
    aromatic: float = Field(
        ge=0.0, le=1.0, description="Intensidad aromática (0.00 - 1.00)"
    )


class BatchPairingItem(BaseModel):
    """Elemento individual de evaluación de afinidad entre un ingrediente A y un candidato B."""

    ingredient_b: str = Field(description="Nombre del ingrediente candidato")
    affinity_score: float = Field(
        ge=0.0, le=1.0, description="Afinidad organoléptica (0.00 - 1.00)"
    )
    ai_rationale: str = Field(
        max_length=300, description="Explicación acotada a máximo 300 caracteres"
    )


class BatchPairingResponse(BaseModel):
    """Respuesta estructurada para evaluación en lote."""

    pairings: list[BatchPairingItem]


class AIExplanationRequest(BaseModel):
    """Solicitud de explicación en prosa para un par o grupo de ingredientes."""

    ingredient_ids: list[int] = Field(min_length=2, max_length=10)


class AIExplanationResponse(BaseModel):
    """Explicación generada o recuperada con provenance explícito."""

    explanation: str
    source: Literal["llm", "stored", "generic"]


class AIReplacementRequest(BaseModel):
    """Solicitud de reemplazo para un ingrediente discordante."""

    target_ingredient_id: int
    other_ingredient_ids: list[int] = Field(min_length=2, max_length=9)


class AIReplacementResponse(BaseModel):
    """Sugerencia de reemplazo gastronómico."""

    suggested_ingredient: str
    rationale: str
    source: Literal["llm", "generic"]
