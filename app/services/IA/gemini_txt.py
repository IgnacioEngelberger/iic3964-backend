"""
Gemini reasoning module for medical urgency evaluation – TEXT ONLY VERSION.
"""

import json
import re
import time
from typing import Any, Dict, List

from app.core.config import settings
from app.schemas.gemini import UrgencyOutput
from app.services.IA.prompts_txt import PROMPT_TMPL, SYSTEM_STRICT

try:
    from google import genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None

client = None
GEN_MODEL = settings.GEMINI_MODEL or "gemini-2.5-flash"

if genai is not None:
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    try:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
    except Exception:
        client = None


def as_user_msg(text: str) -> Dict[str, Any]:
    return {"role": "user", "parts": [{"text": text}]}


def _json_from_text(txt: str) -> Dict[str, Any]:
    """Extract JSON dict from Gemini output text."""
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}\s*$", txt, re.S)
        return json.loads(match.group(0)) if match else {}


def _normalize_hypotheses(raw: Any) -> List[Dict[str, Any]]:
    if not raw:
        return []
    output = []
    for item in raw:
        if isinstance(item, dict):
            cond = item.get("condition") or item.get("diagnosis") or item.get("name")
            conf = item.get("confidence", item.get("score", 0.0))
            try:
                conf = float(conf)
            except Exception:
                conf = 0.0
            if cond:
                output.append(
                    {
                        "condition": cond,
                        "confidence": max(0.0, min(1.0, conf)),
                    }
                )
    return output


def _normalize_citations(raw: Any) -> List[str]:
    if not raw:
        return []
    return [str(x).strip() for x in raw if str(x).strip()][:10]


def _normalize_citations_structured(raw: Any) -> List[Dict[str, Any]]:
    output = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                section = item.get("section", "general")
                if section not in {"urgency", "diagnosis_top", "actions", "general"}:
                    section = "general"
                output.append(
                    {
                        "label": item.get("label", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", ""),
                        "section": section,
                    }
                )
    return output


def _coerce_to_schema(raw: Dict[str, Any]) -> Dict[str, Any]:
    data = dict(raw)
    data.setdefault("urgency_flag", "uncertain")
    data.setdefault("diagnosis_hypotheses", [])
    data.setdefault("rationale", "")
    data.setdefault("actions", [])
    data.setdefault("citations", [])
    data.setdefault("citations_structured", [])

    data["diagnosis_hypotheses"] = _normalize_hypotheses(data["diagnosis_hypotheses"])
    data["citations"] = _normalize_citations(data["citations"])
    data["citations_structured"] = _normalize_citations_structured(
        data["citations_structured"]
    )
    return data


def reason(text: str) -> UrgencyOutput:
    """
    Send raw text about the patient to Gemini and return structured UrgencyOutput.
    The `text` should contain all info: symptoms, history, vitals, timeline, etc.
    """
    if client is None:
        raise RuntimeError(
            "google-genai client is not available. Install 'google-genai' and "
            "configure credentials to use Gemini."
        )

    prompt = PROMPT_TMPL.format(text=text)
    max_attempts = 3
    response = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=GEN_MODEL,
                contents=[as_user_msg(SYSTEM_STRICT), as_user_msg(prompt)],
                config={"response_mime_type": "application/json"},
            )
            break
        except Exception as exc:
            msg = str(exc).lower()
            transient = any(
                x in msg for x in ("503", "unavailable", "overload", "rate")
            )
            if transient and attempt < max_attempts:
                time.sleep(2 ** (attempt - 1))
                continue
            raise

    raw = _json_from_text(response.text or "{}")
    data = _coerce_to_schema(raw)
    return UrgencyOutput(**data)
