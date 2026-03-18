import os
from typing import Any, Dict

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        _client = MongoClient(mongo_uri)
    return _client


def get_db():
    client = get_client()
    db_name = os.getenv("MONGODB_DB", "ai_exam_planner")
    return client[db_name]


def save_plan_document(doc: Dict[str, Any]):
    db = get_db()
    result = db.plans.insert_one(doc)
    return result.inserted_id

