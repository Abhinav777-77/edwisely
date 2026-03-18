from typing import Any, Dict


def merge_performance_and_quiz(
    performance: Dict[str, Any] | None,
    quiz_results: Dict[str, Any] | None,
) -> Dict[str, str]:
    """
    Merge any explicit performance strengths with quiz-based strengths.
    quiz_results is expected to be {"topic_strengths": {topic: strength}}
    """
    merged: Dict[str, str] = {}

    performance = performance or {}
    quiz_results = quiz_results or {}

    # Normalize from various possible shapes into a flat dict
    perf_strengths = performance.get("topic_strengths") if "topic_strengths" in performance else performance
    quiz_strengths = quiz_results.get("topic_strengths") if "topic_strengths" in quiz_results else quiz_results

    for topic, strength in quiz_strengths.items():
        merged[topic] = str(strength)

    for topic, strength_info in perf_strengths.items():
        # strength_info can be "weak" | "medium" | "strong"
        # or a dict like {"strength": "weak", "confidence": 80}
        if isinstance(strength_info, dict):
            strength_value = strength_info.get("strength") or strength_info.get("level") or ""
        else:
            strength_value = str(strength_info)

        if not strength_value:
            continue

        # Explicit performance overrides quiz
        merged[topic] = str(strength_value)

    return merged

