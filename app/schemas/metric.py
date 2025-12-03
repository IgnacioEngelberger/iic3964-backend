from typing import Optional, Union

from pydantic import BaseModel


class MetricStats(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = "Desconocido"

    # 1. Total episodios subidos
    total_episodes: int

    # 2. Ley de urgencia (IA o médico dijeron si) -> applies_urgency_law == True
    total_urgency_law: int
    # % rechazados por aseguradora
    percent_urgency_law_rejected: float

    # 3. Ley de urgencia (IA dijo si) -> ai_result == True
    total_ai_yes: int
    # % rechazados por aseguradora
    percent_ai_yes_rejected: float

    # 4. Ley de urgencia (IA dijo no y médico si)
    total_ai_no_medic_yes: int
    # % rechazados por aseguradora
    percent_ai_no_medic_yes_rejected: float


class MetricsResponse(BaseModel):
    start_date: Optional[str]
    end_date: Optional[str]
    metrics: MetricStats | list[MetricStats]
