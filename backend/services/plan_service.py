from typing import Any, Dict, List

from utils.db import save_plan_document
from utils.gemini_client import generate_plan_with_gemini
from utils.strengths import merge_performance_and_quiz


def generate_plan_service(
    days: int,
    topics: List[Dict[str, Any]],
    performance: Dict[str, Any],
    quiz_results: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Core orchestration for study plan generation.

    Expected topic format from frontend:
    [{"name": "Algebra", "estimated_hours": 5}, ...]

    Performance / quiz_results should map topic -> "strong" | "medium" | "weak".
    """
    topic_strengths = merge_performance_and_quiz(performance, quiz_results)

    # Preserve raw performance details (including confidence) in structured input
    performance_details = performance or {}

    structured_input = {
        "days": days,
        "topics": topics,
        "topic_strengths": topic_strengths,
        "performance_details": performance_details,
        "guidelines": {
            "focus": {
                "weak": 0.5,
                "medium": 0.3,
                "strong": 0.2,
            },
            "include_revision": True,
            "output_format": "day_wise_list_with_topics_and_activity_type",
        },
    }

    ai_plan = generate_plan_with_gemini(structured_input)

    doc = {
        "days": days,
        "topics": topics,
        "topic_strengths": topic_strengths,
        "performance_details": performance_details,
        "ai_plan": ai_plan,
    }
    plan_id = save_plan_document(doc)

    return {"plan_id": str(plan_id), "plan": ai_plan}

