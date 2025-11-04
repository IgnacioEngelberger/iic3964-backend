from uuid import UUID

from app.core.supabase_client import supabase
from app.services.IA.gemini_txt import reason as ai_reasoner


def run_ai_reasoning_task(attention_id: UUID, diagnostic: str):
    """
    Background task to process IA reasoning and update DB.
    Runs async to avoid blocking API responses.
    """
    try:
        print(f"[AI Task] Starting Gemini reasoning for attention {attention_id}")

        ai_output = ai_reasoner(diagnostic)  # Expensive call

        # Correct field extraction
        urgency_flag = ai_output.urgency_flag  # "applies"
        applies_law = urgency_flag == "applies"

        supabase.table("ClinicalAttention").update(
            {
                "applies_urgency_law": applies_law,  # boolean
                "ai_result": True,  # short string
                "ai_reason": ai_output.rationale,  # detailed JSON string
            }
        ).eq("id", str(attention_id)).execute()

        print(f"[AI Task] ✅ Updated IA result for attention {attention_id}")

    except Exception as e:
        print(f"[AI Task] ❌ Error processing IA for {attention_id}: {e}")
