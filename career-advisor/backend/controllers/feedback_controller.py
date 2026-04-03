# controllers/feedback_controller.py

from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

# Optional DB (replace later)
# from models.feedback_model import db, Feedback

# ---------------------------
# BLUEPRINT
# ---------------------------
feedback_bp = Blueprint('feedback_controller', __name__, url_prefix='/api/feedback')

# ---------------------------
# LOGGER
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# TEMP STORAGE
# ---------------------------
FEEDBACKS = []

# ---------------------------
# RESPONSE HELPER
# ---------------------------
def api_response(success=True, message="", data=None, error=None, status=200):
    return jsonify({
        "success": success,
        "message": message,
        "data": data,
        "error": error
    }), status


# ---------------------------
# SUBMIT FEEDBACK
# ---------------------------
@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()

        feedback = {
            "id": len(FEEDBACKS) + 1,
            "user_id": data.get("user_id"),
            "rating": data.get("rating"),
            "comment": data.get("comment"),
            "created_at": datetime.utcnow().isoformat()
        }

        FEEDBACKS.append(feedback)

        return api_response(True, "Feedback submitted", feedback, status=201)

    except Exception as e:
        return api_response(False, "Submission failed", error=str(e), status=500)


# ---------------------------
# GET ALL FEEDBACK
# ---------------------------
@feedback_bp.route("/", methods=["GET"])
def get_all_feedback():
    try:
        return api_response(True, "All feedback fetched", FEEDBACKS)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# GET FEEDBACK BY USER
# ---------------------------
@feedback_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_feedback(user_id):
    try:
        user_feedback = [f for f in FEEDBACKS if f["user_id"] == user_id]

        return api_response(True, "User feedback", user_feedback)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# UPDATE FEEDBACK
# ---------------------------
@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
def update_feedback(feedback_id):
    try:
        data = request.get_json()

        feedback = next((f for f in FEEDBACKS if f["id"] == feedback_id), None)

        if not feedback:
            return api_response(False, "Feedback not found", status=404)

        feedback["rating"] = data.get("rating", feedback["rating"])
        feedback["comment"] = data.get("comment", feedback["comment"])

        return api_response(True, "Feedback updated", feedback)

    except Exception as e:
        return api_response(False, "Update failed", error=str(e), status=500)


# ---------------------------
# DELETE FEEDBACK
# ---------------------------
@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
def delete_feedback(feedback_id):
    try:
        global FEEDBACKS

        FEEDBACKS = [f for f in FEEDBACKS if f["id"] != feedback_id]

        return api_response(True, "Feedback deleted")

    except Exception as e:
        return api_response(False, "Delete failed", error=str(e), status=500)


# ---------------------------
# GET AVERAGE RATING
# ---------------------------
@feedback_bp.route("/average", methods=["GET"])
def average_rating():
    try:
        if not FEEDBACKS:
            return api_response(True, "No feedback yet", {"average": 0})

        avg = sum(f["rating"] for f in FEEDBACKS) / len(FEEDBACKS)

        return api_response(True, "Average rating", {
            "average": round(avg, 2)
        })

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# FILTER GOOD FEEDBACK
# ---------------------------
@feedback_bp.route("/good", methods=["GET"])
def good_feedback():
    try:
        good = [f for f in FEEDBACKS if f["rating"] >= 4]

        return api_response(True, "Positive feedback", good)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# FILTER BAD FEEDBACK
# ---------------------------
@feedback_bp.route("/bad", methods=["GET"])
def bad_feedback():
    try:
        bad = [f for f in FEEDBACKS if f["rating"] <= 2]

        return api_response(True, "Negative feedback", bad)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# FEEDBACK STATS
# ---------------------------
@feedback_bp.route("/stats", methods=["GET"])
def feedback_stats():
    try:
        stats = {
            "total": len(FEEDBACKS),
            "5_star": len([f for f in FEEDBACKS if f["rating"] == 5]),
            "4_star": len([f for f in FEEDBACKS if f["rating"] == 4]),
            "3_star": len([f for f in FEEDBACKS if f["rating"] == 3]),
            "2_star": len([f for f in FEEDBACKS if f["rating"] == 2]),
            "1_star": len([f for f in FEEDBACKS if f["rating"] == 1])
        }

        return api_response(True, "Feedback stats", stats)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# SEARCH FEEDBACK
# ---------------------------
@feedback_bp.route("/search", methods=["GET"])
def search_feedback():
    try:
        query = request.args.get("q", "").lower()

        results = [
            f for f in FEEDBACKS
            if query in f["comment"].lower()
        ]

        return api_response(True, "Search results", results)

    except Exception as e:
        return api_response(False, "Search failed", error=str(e), status=500)


# ---------------------------
# END (~300 lines)
# ---------------------------
