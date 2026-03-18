from flask import Blueprint, jsonify, request

from services.quiz_service import get_quiz_questions, evaluate_quiz

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.post("/questions")
def questions():
    data = request.get_json(force=True) or {}
    topics = data.get("topics", [])
    questions_payload = get_quiz_questions(topics=topics)
    return jsonify(questions_payload), 200


@quiz_bp.post("/evaluate")
def evaluate():
    data = request.get_json(force=True) or {}
    answers = data.get("answers", [])
    topics = data.get("topics", [])

    results = evaluate_quiz(answers=answers, topics=topics)
    return jsonify(results), 200

