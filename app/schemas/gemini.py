from typing import Any, Dict, List, Optional, Literal
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
    symptoms: str
    vitals: Optional[str] = None
    age: Optional[str] = None
    comorbidities: Optional[str] = None
    onset: Optional[str] = None

class UrgencyOutput(BaseModel):
    urgency_flag: Literal["applies", "uncertain", "does_not_apply"]
    diagnosis_hypotheses: List[Dx]
    rationale: str
    actions: List[str]
    citations: List[str] = []
    citations_structured: List[CitationObj] = []