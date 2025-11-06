"""
Pydantic models for Gemini Urgency input and output schemas.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


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
        example="Dolor torácico intenso y sudoración profusa",
    )
    vitals: Optional[str] = Field(
        None,
        example="TA 90/60, FC 110, SatO2 96%",
    )
    age: Optional[str] = Field(
        None,
        example="67",
    )
    comorbidities: Optional[str] = Field(
        None,
        example="hipertensión, diabetes",
    )
    onset: Optional[str] = Field(
        None,
        example="2 horas",
    )

    class Config:
        schema_extra = {
            "example": {
                "symptoms": "Dolor torácico intenso y sudoración profusa",
                "vitals": "TA 90/60, FC 110, SatO2 96%",
                "age": "67",
                "comorbidities": "hipertensión, diabetes",
                "onset": "2 horas",
            }
        }


class UrgencyOutput(BaseModel):
    """Model returned after Gemini reasoning about Ley de Urgencia."""

    urgency_flag: Literal["applies", "uncertain", "does_not_apply"]
    diagnosis_hypotheses: List[Dx]
    rationale: str
    actions: List[str]
    citations: List[str] = Field(default_factory=list)
    citations_structured: List[CitationObj] = Field(default_factory=list)

    class Config:
        schema_extra = {
            "example": {
                "urgency_flag": "applies",
                "diagnosis_hypotheses": [],
                "rationale": (
                    "Paciente con dolor torácico intenso, sudoración profusa, "
                    "hipotensión (TA 90/60) y taquicardia (FC 110). Antecedentes: "
                    "HTA y diabetes. Cuadro de 2 horas de evolución. Sugiere evento "
                    "cardiovascular agudo con riesgo vital o secuela grave. Requiere "
                    "atención inmediata. Corresponde activar Ley de Urgencia."
                ),
                "actions": [
                    "Activar Ley de Urgencia",
                    "Traslado a centro de alta complejidad",
                    "Estabilización y evaluación de emergencia",
                ],
                "citations": [],
                "citations_structured": [],
            }
        }
