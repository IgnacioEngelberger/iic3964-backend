"""
Pydantic models for Gemini Urgency input and output schemas.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class Dx(BaseModel):
    """Single diagnostic hypothesis with confidence score."""

    condition: str
    confidence: float = Field(ge=0, le=1)


class CitationObj(BaseModel):
    """Structured reference to a medical/legal source."""

    label: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    section: Literal["urgency", "diagnosis_top", "actions", "general"] = "general"


class UrgencyInput(BaseModel):
    """Input payload expected by the Gemini urgency endpoint.

    All fields are strings so the prompt formatting is straightforward;
    many can be left empty or omitted if unknown.
    """

    symptoms: str = Field(
        ...,
        json_schema_extra={"example": "Dolor torácico intenso y sudoración profusa"},
    )
    vitals: Optional[str] = Field(
        None,
        json_schema_extra={"example": "TA 90/60, FC 110, SatO2 96%"},
    )
    age: Optional[str] = Field(
        None,
        json_schema_extra={"example": "67"},
    )
    comorbidities: Optional[str] = Field(
        None,
        json_schema_extra={"example": "hipertensión, diabetes"},
    )
    onset: Optional[str] = Field(
        None,
        json_schema_extra={"example": "2 horas"},
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symptoms": "Dolor torácico intenso y sudoración profusa",
                "vitals": "TA 90/60, FC 110, SatO2 96%",
                "age": "67",
                "comorbidities": "hipertensión, diabetes",
                "onset": "2 horas",
            }
        }
    )


class UrgencyOutput(BaseModel):
    """Model returned after Gemini reasoning about Ley de Urgencia."""

    urgency_flag: Literal["applies", "uncertain", "does_not_apply"]
    urgency_confidence: float = Field(default=0.0, ge=0, le=1)
    diagnosis_hypotheses: List[Dx]
    rationale: str
    actions: List[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "urgency_flag": "applies",
                "urgency_confidence": 0.92,
                "diagnosis_hypotheses": [],
                "rationale": (
                    "Paciente con dolor torácico intenso, sudoración profusa, "
                    "hipotensión y taquicardia. Cuadro sugiere evento cardiovascular "
                    "agudo con riesgo vital. Corresponde activar Ley de Urgencia."
                ),
                "actions": [
                    "Activar Ley de Urgencia",
                    "Traslado inmediato",
                    "Estabilización inicial",
                ],
            }
        }
    )
