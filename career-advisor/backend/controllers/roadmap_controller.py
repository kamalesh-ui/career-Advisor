# controllers/roadmap_controller.py

from flask import Blueprint, request, jsonify
from models.user_model import db, User
from models.career_model import Career
from models.progress_model import Progress
import logging

# ---------------------------
# BLUEPRINT
# ---------------------------
roadmap_bp = Blueprint('roadmap_controller', __name__, url_prefix='/api/roadmap')

# ---------------------------
# LOGGER
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
# STATIC ROADMAP TEMPLATES
# ---------------------------
ROADMAP_TEMPLATES = {
    "Software Developer": [
        "Learn Programming Basics",
        "Learn Python / JavaScript",
        "Understand Data Structures",
        "Build Mini Projects",
        "Learn Backend / Frontend",
        "Build Full Stack Project",
        "Prepare Resume",
        "Apply for Jobs"
    ],
    "Data Analyst": [
        "Learn Excel",
        "Learn Python (Pandas, NumPy)",
        "Learn SQL",
        "Data Visualization (Power BI/Tableau)",
        "Build Projects",
        "Prepare Portfolio",
        "Apply for Jobs"
    ]
}

# ---------------------------
# GENERATE ROADMAP
# ---------------------------
@roadmap_bp.route("/generate", methods=["POST"])
def generate_roadmap():
    try:
        data = request.get_json()

        career_name = data.get("career")

        if not career_name:
            return api_response(False, "Career required", status=400)

        roadmap = ROADMAP_TEMPLATES.get(career_name)

        if not roadmap:
            # Default roadmap
            roadmap = [
                "Learn Basics",
                "Practice Skills",
                "Build Projects",
                "Get Certified",
                "Apply for Jobs"
            ]

        return api_response(True, "Roadmap generated", {
            "career": career_name,
            "steps": roadmap,
            "total_steps": len(roadmap)
        })

    except Exception as e:
        return api_response(False, "Error generating roadmap", error=str(e), status=500)


# ---------------------------
# SAVE USER ROADMAP
# ---------------------------
@roadmap_bp.route("/save", methods=["POST"])
def save_roadmap():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        career_id = data.get("career_id")

        progress = Progress(
            user_id=user_id,
            career_id=career_id,
            progress_percent=0
        )

        db.session.add(progress)
        db.session.commit()

        return api_response(True, "Roadmap saved")

    except Exception as e:
        return api_response(False, "Error saving roadmap", error=str(e), status=500)


# ---------------------------
# GET USER ROADMAP
# ---------------------------
@roadmap_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_roadmap(user_id):
    try:
        progress = Progress.query.filter_by(user_id=user_id).all()

        data = [p.to_dict() for p in progress]

        return api_response(True, "User roadmap fetched", data)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# UPDATE PROGRESS
# ---------------------------
@roadmap_bp.route("/update", methods=["PUT"])
def update_progress():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        career_id = data.get("career_id")
        completed_steps = data.get("completed_steps", [])
        total_steps = data.get("total_steps", 1)

        progress = Progress.query.filter_by(
            user_id=user_id,
            career_id=career_id
        ).first()

        if not progress:
            return api_response(False, "Progress not found", status=404)

        progress.set_completed_steps(completed_steps)
        progress.update_progress(len(completed_steps), total_steps)

        db.session.commit()

        return api_response(True, "Progress updated", progress.to_dict())

    except Exception as e:
        return api_response(False, "Update failed", error=str(e), status=500)


# ---------------------------
# GET PROGRESS PERCENT
# ---------------------------
@roadmap_bp.route("/progress/<int:user_id>", methods=["GET"])
def get_progress(user_id):
    try:
        progress = Progress.query.filter_by(user_id=user_id).all()

        result = []

        for p in progress:
            result.append({
                "career_id": p.career_id,
                "progress": p.progress_percent
            })

        return api_response(True, "Progress fetched", result)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# NEXT STEP SUGGESTION
# ---------------------------
@roadmap_bp.route("/next-step", methods=["POST"])
def next_step():
    try:
        data = request.get_json()

        career_name = data.get("career")
        completed = data.get("completed_steps", [])

        roadmap = ROADMAP_TEMPLATES.get(career_name, [])

        for step in roadmap:
            if step not in completed:
                return api_response(True, "Next step", {
                    "next_step": step
                })

        return api_response(True, "All steps completed 🎉")

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# RESET PROGRESS
# ---------------------------
@roadmap_bp.route("/reset", methods=["POST"])
def reset_progress():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        career_id = data.get("career_id")

        progress = Progress.query.filter_by(
            user_id=user_id,
            career_id=career_id
        ).first()

        if progress:
            progress.progress_percent = 0
            progress.completed_steps = ""
            db.session.commit()

        return api_response(True, "Progress reset")

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# DELETE ROADMAP
# ---------------------------
@roadmap_bp.route("/delete", methods=["DELETE"])
def delete_roadmap():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        career_id = data.get("career_id")

        progress = Progress.query.filter_by(
            user_id=user_id,
            career_id=career_id
        ).first()

        if progress:
            db.session.delete(progress)
            db.session.commit()

        return api_response(True, "Roadmap deleted")

    except Exception as e:
        return api_response(False, "Delete failed", error=str(e), status=500)


# ---------------------------
# DASHBOARD SUMMARY
# ---------------------------
@roadmap_bp.route("/summary/<int:user_id>", methods=["GET"])
def summary(user_id):
    try:
        progress_list = Progress.query.filter_by(user_id=user_id).all()

        total = len(progress_list)
        completed = sum(1 for p in progress_list if p.progress_percent == 100)

        return api_response(True, "Summary", {
            "total_roadmaps": total,
            "completed": completed
        })

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# END (~300 lines)
# ---------------------------