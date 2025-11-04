from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Dx(BaseModel):
    condition: str
    confidence: float = Field(ge=0, le=1)


class CitationObj(BaseModel):
    label: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    section: Literal["urgency", "diagnosis_top", "actions", "general"] = "general"


class UrgencyInput(BaseModel):
    """Input payload expected by the Gemini urgency endpoint.

    All fields are strings so the prompt formatting is straightforward; many
    can be left empty or omitted if unknown.
    """

    symptoms: str = Field(..., examples=["Dolor torácico intenso y sudoración profusa"])
    vitals: Optional[str] = Field(None, examples=["TA 90/60, FC 110, SatO2 96%"])
    age: Optional[str] = Field(None, examples=["67"])
    comorbidities: Optional[str] = Field(None, examples=["hipertensión, diabetes"])
    onset: Optional[str] = Field(None, examples=["2 horas"])

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
                    "El paciente presenta dolor torácico intenso, sudoración profusa, "
                    "hipotensión (TA 90/60) y taquicardia (FC 110), con antecedentes "
                    "de hipertensión y diabetes, y una evolución de 2 horas. "
                    "Estos signos y síntomas son altamente sugerentes de un evento "
                    "cardiovascular agudo grave, como un Infarto Agudo al Miocardio "
                    "o una Disección Aórtica, los cuales constituyen un riesgo "
                    "inminente de muerte o secuela funcional grave que requiere "
                    "atención inmediata e impostergable. Por lo tanto, cumple con "
                    "los criterios para la aplicación de la Ley de Urgencia en Chile."
                ),
                "actions": [
                    "Activar Ley de Urgencia",
                    (
                        "Solicitar traslado inmediato a un centro asistencial "
                        "de alta complejidad"
                    ),
                    "Estabilización inicial y evaluación médica de emergencia",
                ],
                "citations": [],
                "citations_structured": [],
            }
        }
