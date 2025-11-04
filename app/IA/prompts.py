SYSTEM = (
    "Eres un asistente clínico-legal en Chile. Usa SOLO los pasajes recuperados "
    "para evaluar Ley de Urgencia (riesgo de muerte o secuela funcional grave "
    "que requiera atención inmediata e impostergable). Devuelve "
    "EXCLUSIVAMENTE JSON válido."
)

SYSTEM_STRICT = SYSTEM + (
    "\n\nResponde EXACTAMENTE con este esquema JSON:"
    '\n{\n  "urgency_flag": "applies|uncertain|does_not_apply",'
    '\n  "Sdiagnosis_hypotheses": [{"condition": "str", "confidence": 0.0}],'
    '\n  "rationale": "str",'
    '\n  "actions": ["str", "..."],'
    '\n  "citations": ["str", "..."],'
    '\n  "citations_structured": ['
    '\n    {"label":"str", "url":"str", "snippet":"str", '
    '"section":"urgency|diagnosis_top|actions|general"}'
    "\n  ]\n}\n"
)

PROMPT_TMPL = """\
Paciente:
- Síntomas: {symptoms}
- Signos vitales: {vitals}
- Edad: {age}
- Comorbilidades: {comorbidities}
- Tiempo de evolución: {onset}

Instrucciones:
1) 2–5 hipótesis diagnósticas con confianza [0–1].
2) urgency_flag: "applies" si hay riesgo vital/secuela grave que requiere
    atención inmediata; "does_not_apply" si no; "uncertain" si falta info.
3) Acciones inmediatas (p.ej., activar 131 / activar Ley de Urgencia) si
    corresponde.
4) Devuelve SOLO JSON válido del esquema indicado.
"""
