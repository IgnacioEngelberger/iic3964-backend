from fastapi import APIRouter, HTTPException

from app.schemas.gemini import UrgencyInput, UrgencyOutput
from app.services.IA import gemini as gemini_module

router = APIRouter()


@router.post("/reason", response_model=UrgencyOutput)
def reason(payload: UrgencyInput):
    """Evaluate urgency using Gemini.

    Expects a JSON body matching `UrgencyInput` and returns `UrgencyOutput`.
    """
    try:
        result = gemini_module.reason(payload.dict())
        return result
    except RuntimeError as e:
        # Explicit runtime error when google-genai client is missing
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini evaluation failed: {e}")
