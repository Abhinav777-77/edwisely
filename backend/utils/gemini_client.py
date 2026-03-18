import os
import json
import re
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)


def generate_plan_with_gemini(structured_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call Google Gemini with a structured prompt and return a JSON plan.
    If GEMINI_API_KEY is not configured, fall back to a deterministic local plan.
    """
    if not API_KEY:
        return _fallback_plan(structured_input)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are an AI exam preparation planner.

Input JSON (days, topics, topic_strengths, and optional performance_details with confidence scores):
{json.dumps(structured_input, indent=2)}

Goals:
- For each high-level subject/topic, expand into concrete subtopics (for example, for "Data Structures" include arrays, linked lists, stacks, queues, trees, graphs, hashing, etc.).
- Use strengths ("weak" / "medium" / "strong") and confidence to allocate more learning/practice time to weak/low-confidence areas, while still including revision for strong topics.
- Distribute subtopics clearly across the available days, mixing concept learning, practice, and revision.

Respond ONLY with valid JSON in this shape:
{{ "days": [{{"day": 1, "items": [{{"topic": "str", "focus": "learning|practice|revision", "notes": "str"}}]}}] }}
Where "topic" should usually be a specific subtopic (e.g. "Binary Trees", "Graph BFS") rather than only the coarse subject name.
"""

    response = model.generate_content(prompt)
    print(response)
    try:
        text = response.text or ""

        # Safer JSON extraction (Gemini may add extra text around the JSON)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())

        return _fallback_plan(structured_input)

    except Exception:
        return _fallback_plan(structured_input)


def _fallback_plan(structured_input: Dict[str, Any]) -> Dict[str, Any]:
    days = structured_input.get("days", 1)
    topics = structured_input.get("topics", [])
    strengths = structured_input.get("topic_strengths", {})

    if not topics:
        return {"days": []}

    plan_days = []
    # Simple round-robin over topics with note on strength
    for day_idx in range(days):
        items = []
        topic = topics[day_idx % len(topics)]
        name = topic.get("name", f"Topic {day_idx + 1}")
        strength = strengths.get(name, "medium")
        if strength == "weak":
            focus = "learning"
            notes = "Spend extra time understanding core concepts and doing basic practice."
        elif strength == "medium":
            focus = "practice"
            notes = "Do a mix of problems and short revisions."
        else:
            focus = "revision"
            notes = "Quick revision and a few higher-level questions."

        items.append({"topic": name, "focus": focus, "notes": notes})
        plan_days.append({"day": day_idx + 1, "items": items})

    return {"days": plan_days}


def generate_quiz_with_gemini(topics: List[str]) -> Dict[str, Any]:
    """
    Generate quiz questions dynamically using Gemini for unknown topics.
    Returns same structure as get_quiz_questions()
    """

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are an AI quiz generator.

Generate a small quiz for the following topics:
{topics}

Rules:
- Generate 1–2 questions per topic
- Each question must have 4 options
- Provide correct_index (0-based)
- Keep questions simple and conceptual

Respond ONLY with valid JSON in this format:
{{
  "questions": [
    {{
      "id": 1,
      "topic": "topic name",
      "question": "string",
      "options": ["A", "B", "C", "D"],
      "correct_index": 0
    }}
  ]
}}
"""

    response = model.generate_content(prompt)

    try:
        text = response.text or ""

        # Extract JSON safely
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group())

            # Ensure IDs are correct sequence
            for i, q in enumerate(data.get("questions", []), start=1):
                q["id"] = i

            return data

        return {"questions": []}

    except Exception:
        return {"questions": []}