from typing import Any, Dict, List

from utils.gemini_client import generate_quiz_with_gemini
def _basic_question_bank() -> Dict[str, List[Dict[str, Any]]]:
    """
    Very small, basic question templates for common CS/Math topics.
    Falls back to generic questions when topic not recognized.
    """
    return {
        "data structures": [
            {
                "question": "Which data structure works on FIFO order?",
                "options": ["Stack", "Queue", "Tree", "Graph"],
                "correct_index": 1,
            },
            {
                "question": "Which traversal is typically used for BFS?",
                "options": ["Queue", "Stack", "Recursion only", "Sorting"],
                "correct_index": 0,
            },
        ],
        "algorithms": [
            {
                "question": "What is the time complexity of binary search?",
                "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
                "correct_index": 1,
            }
        ],
        "dbms": [
            {
                "question": "Which SQL clause is used to filter rows?",
                "options": ["WHERE", "ORDER BY", "GROUP BY", "JOIN"],
                "correct_index": 0,
            }
        ],
        "operating systems": [
            {
                "question": "What does a CPU scheduler decide?",
                "options": ["Which process runs next", "Disk partition size", "RAM speed", "Network routing"],
                "correct_index": 0,
            }
        ],
        "networks": [
            {
                "question": "Which protocol is used to reliably deliver data over the internet?",
                "options": ["UDP", "TCP", "ICMP", "ARP"],
                "correct_index": 1,
            }
        ],
        "calculus": [
            {
                "question": "Derivative of x^2 is?",
                "options": ["2x", "x", "x^2", "1"],
                "correct_index": 0,
            }
        ],
        "physics": [
            {
                "question": "Unit of force is?",
                "options": ["Joule", "Newton", "Watt", "Pascal"],
                "correct_index": 1,
            }
        ],
        "algebra": [
            {
                "question": "Solve: 2x + 3 = 11",
                "options": ["x = 4", "x = 3", "x = 5", "x = 6"],
                "correct_index": 0,
            }
        ],
    }


def get_quiz_questions(topics: List[str]) -> Dict[str, Any]:
    """
    Generate a small basic quiz based on user-provided topics.
    topics: list of topic/subject names entered by the student.
    """
    topics = [t.strip() for t in (topics or []) if isinstance(t, str) and t.strip()]
    bank = _basic_question_bank()

    questions: List[Dict[str, Any]] = []
    qid = 1

    for raw_topic in topics[:10]:
        key = raw_topic.lower().strip()
        templates = bank.get(key)

        # Loose matching for common phrases (e.g., "DS", "Data Structures and Algorithms")
        if templates is None:
            if "data structure" in key or key in {"ds", "dsa"}:
                templates = bank["data structures"]
                raw_topic = "Data Structures"
            elif "algorithm" in key:
                templates = bank["algorithms"]
                raw_topic = "Algorithms"
            elif "operating" in key or key in {"os"}:
                templates = bank["operating systems"]
                raw_topic = "Operating Systems"
            elif "network" in key or key in {"cn"}:
                templates = bank["networks"]
                raw_topic = "Networks"
            elif "dbms" in key or "database" in key:
                templates = bank["dbms"]
                raw_topic = "DBMS"

        if not templates:
            # 🔥 Call Gemini instead of fallback question
            gemini_quiz = generate_quiz_with_gemini([raw_topic])

            for q in gemini_quiz.get("questions", []):
                questions.append(q)
                qid += 1

            continue

        # Pick up to 2 questions per topic for speed
        for t in templates[:2]:
            questions.append(
                {
                    "id": qid,
                    "topic": raw_topic,
                    "question": t["question"],
                    "options": t["options"],
                    "correct_index": int(t["correct_index"]),
                }
            )
            qid += 1

    return {"questions": questions}


def evaluate_quiz(answers: List[Dict[str, Any]], topics: List[str]) -> Dict[str, Any]:
    """
    Very simple evaluation: overall score + per-topic confidence (0-100) + strength bucket.
    answers: [{"id": 1, "selected_index": 0, "correct_index": 0, "topic": "Algebra"}, ...]
    """
    topic_correct = {}
    topic_total = {}
    overall_total = 0
    overall_correct = 0

    for ans in answers:
        topic = ans.get("topic")
        if not topic:
            continue
        topic_total[topic] = topic_total.get(topic, 0) + 1
        overall_total += 1
        if ans.get("selected_index") == ans.get("correct_index"):
            topic_correct[topic] = topic_correct.get(topic, 0) + 1
            overall_correct += 1

    topic_strengths: Dict[str, str] = {}
    topic_confidence: Dict[str, int] = {}
    all_topics = set(topics) | set(topic_total.keys())

    for topic in all_topics:
        total = topic_total.get(topic, 0)
        correct = topic_correct.get(topic, 0)
        accuracy = correct / total if total > 0 else 0.0

        confidence = int(round(accuracy * 100))
        topic_confidence[topic] = confidence

        if accuracy >= 0.8:
            topic_strengths[topic] = "strong"
        elif accuracy >= 0.5:
            topic_strengths[topic] = "medium"
        else:
            topic_strengths[topic] = "weak"

    overall_score = int(round((overall_correct / overall_total) * 100)) if overall_total > 0 else 0

    return {
        "score": overall_score,
        "topic_strengths": topic_strengths,
        "topic_confidence": topic_confidence,
    }

