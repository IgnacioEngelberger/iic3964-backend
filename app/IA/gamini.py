import re, json, html, time
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
from app.schemas.gemini import UrgencyOutput
from app.core.config import settings

try:
    from google import genai  # type: ignore
except Exception:  # pragma: no cover - runtime environment may not have google-genai
    genai = None

# Lazy-initialize client if genai is available and API key is configured
client = None
GEN_MODEL = settings.GEMINI_MODEL or "gemini-2.5-flash"
if genai is not None:
    api_key = getattr(settings, "GEMINI_API_KEY", None)
    try:
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            # allow default client creation (e.g., ADC or other env vars)
            client = genai.Client()
    except Exception:
        client = None

from app.IA.prompts import SYSTEM_STRICT, PROMPT_TMPL
def as_user_msg(text: str) -> dict:
    return {"role": "user", "parts": [{"text": text}]}

# --- Normalize and parse Gemini output ---
def _json_from_text(txt: str) -> Dict[str, Any]:
    try:
        return json.loads(txt)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}\s*$", txt, re.S)
        return json.loads(m.group(0)) if m else {}

def _normalize_hypotheses(h: Any) -> List[Dict[str, Any]]:
    if not h: return []
    out = []
    for item in h:
        if isinstance(item, dict):
            cond = item.get("condition") or item.get("diagnosis") or item.get("name")
            conf = item.get("confidence", item.get("score", 0.0))
            try: conf = float(conf)
            except: conf = 0.0
            if cond:
                out.append({"condition": cond, "confidence": max(0.0, min(1.0, conf))})
    return out

def _normalize_citations(c: Any) -> List[str]:
    if not c: return []
    return [str(x).strip() for x in c if str(x).strip()][:10]

def _normalize_citations_structured(c: Any) -> List[Dict[str, Any]]:
    out = []
    if isinstance(c, list):
        for item in c:
            if isinstance(item, dict):
                section = item.get("section", "general")
                if section not in {"urgency","diagnosis_top","actions","general"}:
                    section = "general"
                out.append({
                    "label": item.get("label", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("snippet", ""),
                    "section": section
                })
    return out

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
    data["citations_structured"] = _normalize_citations_structured(data["citations_structured"])
    return data

def reason(case: dict) -> UrgencyOutput:
    prompt = PROMPT_TMPL.format(**case)
    # print("Gemini prompt:", prompt)

    if client is None:
        raise RuntimeError("google-genai client is not available. Install 'google-genai' and configure credentials to use Gemini.")

    # Retry on transient server-side errors (e.g., 503 overloaded)
    max_attempts = 3
    resp = None
    last_exc = None
    for attempt in range(1, max_attempts + 1):
        try:
            resp = client.models.generate_content(
                model=GEN_MODEL,
                contents=[as_user_msg(SYSTEM_STRICT), as_user_msg(prompt)],
                config={"response_mime_type": "application/json"}
            )
            break
        except Exception as e:
            last_exc = e
            msg = str(e)
            # if it's a transient server-side error, retry with exponential backoff
            if any(tok in msg for tok in ("503", "UNAVAILABLE", "overload", "overloaded", "rate")):
                if attempt < max_attempts:
                    wait = 2 ** (attempt - 1)
                    time.sleep(wait)
                    continue
                else:
                    raise RuntimeError(f"Gemini service unavailable after {max_attempts} attempts: {e}")
            # non-transient error, re-raise
            raise

    raw = _json_from_text(resp.text or "{}")
    data = _coerce_to_schema(raw)
    return UrgencyOutput(**data)