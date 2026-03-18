from flask import Blueprint, request, jsonify

from services.plan_service import generate_plan_service

plan_bp = Blueprint("plan", __name__)


@plan_bp.post("/generate")
def generate_plan():
    data = request.get_json(force=True) or {}

    try:
        days = int(data.get("days", 0))
    except (TypeError, ValueError):
        days = 0

    topics = data.get("topics", [])
    performance = data.get("performance") or {}
    quiz_results = data.get("quiz_results")

    if days <= 0 or not topics:
        return jsonify({"error": "days and topics are required"}), 400

    try:
        plan = generate_plan_service(days=days, topics=topics, performance=performance, quiz_results=quiz_results)
        return jsonify(plan), 200
    except Exception as exc:  # pragma: no cover - simple prototype error handling
        return jsonify({"error": str(exc)}), 500

