# controllers/career_controller.py

from flask import Blueprint, request, jsonify
from models.user_model import db
from datetime import datetime
import logging

# If you create separate model later, import here
# from models.career_model import Career

# ---------------------------
# BLUEPRINT
# ---------------------------
career_bp = Blueprint('career_controller', __name__, url_prefix='/api/careers')

# ---------------------------
# LOGGER
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# TEMP STORAGE (Replace with DB later)
# ---------------------------
CAREERS = [
    {
        "id": 1,
        "title": "Software Developer",
        "description": "Build applications and systems",
        "skills": ["python", "javascript", "sql"],
        "domain": "IT"
    },
    {
        "id": 2,
        "title": "Data Analyst",
        "description": "Analyze data and generate insights",
        "skills": ["excel", "python", "statistics"],
        "domain": "Data"
    },
    {
        "id": 3,
        "title": "UI/UX Designer",
        "description": "Design user interfaces",
        "skills": ["figma", "design", "creativity"],
        "domain": "Design"
    }
]

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
# GET ALL CAREERS
# ---------------------------
@career_bp.route("/", methods=["GET"])
def get_all_careers():
    try:
        return api_response(True, "Careers fetched", CAREERS)

    except Exception as e:
        return api_response(False, "Error fetching careers", error=str(e), status=500)


# ---------------------------
# GET CAREER BY ID
# ---------------------------
@career_bp.route("/<int:career_id>", methods=["GET"])
def get_career(career_id):
    try:
        career = next((c for c in CAREERS if c["id"] == career_id), None)

        if not career:
            return api_response(False, "Career not found", status=404)

        return api_response(True, "Career fetched", career)

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# SEARCH CAREERS
# ---------------------------
@career_bp.route("/search", methods=["GET"])
def search_careers():
    try:
        query = request.args.get("q", "").lower()

        results = [
            c for c in CAREERS
            if query in c["title"].lower() or query in c["domain"].lower()
        ]

        return api_response(True, "Search results", results)

    except Exception as e:
        return api_response(False, "Search failed", error=str(e), status=500)


# ---------------------------
# ADD NEW CAREER (ADMIN)
# ---------------------------
@career_bp.route("/", methods=["POST"])
def add_career():
    try:
        data = request.get_json()

        new_career = {
            "id": len(CAREERS) + 1,
            "title": data.get("title"),
            "description": data.get("description"),
            "skills": data.get("skills", []),
            "domain": data.get("domain")
        }

        CAREERS.append(new_career)

        return api_response(True, "Career added", new_career, status=201)

    except Exception as e:
        return api_response(False, "Error adding career", error=str(e), status=500)


# ---------------------------
# UPDATE CAREER
# ---------------------------
@career_bp.route("/<int:career_id>", methods=["PUT"])
def update_career(career_id):
    try:
        data = request.get_json()

        career = next((c for c in CAREERS if c["id"] == career_id), None)

        if not career:
            return api_response(False, "Career not found", status=404)

        career["title"] = data.get("title", career["title"])
        career["description"] = data.get("description", career["description"])
        career["skills"] = data.get("skills", career["skills"])
        career["domain"] = data.get("domain", career["domain"])

        return api_response(True, "Career updated", career)

    except Exception as e:
        return api_response(False, "Update failed", error=str(e), status=500)


# ---------------------------
# DELETE CAREER
# ---------------------------
@career_bp.route("/<int:career_id>", methods=["DELETE"])
def delete_career(career_id):
    try:
        global CAREERS

        CAREERS = [c for c in CAREERS if c["id"] != career_id]

        return api_response(True, "Career deleted")

    except Exception as e:
        return api_response(False, "Delete failed", error=str(e), status=500)


# ---------------------------
# SKILL MATCHING LOGIC
# ---------------------------
def calculate_match(user_skills, career_skills):
    if not user_skills or not career_skills:
        return 0

    user_set = set(user_skills)
    career_set = set(career_skills)

    match = user_set.intersection(career_set)

    score = (len(match) / len(career_set)) * 100

    return round(score, 2)


# ---------------------------
# AI RECOMMENDATIONS
# ---------------------------
@career_bp.route("/recommend", methods=["POST"])
def recommend_careers():
    try:
        data = request.get_json()

        user_skills = data.get("skills", [])
        user_interests = data.get("interests", [])

        results = []

        for career in CAREERS:
            score = calculate_match(user_skills, career["skills"])

            # Interest boost
            if career["domain"].lower() in [i.lower() for i in user_interests]:
                score += 10

            results.append({
                "career": career["title"],
                "match_score": min(score, 100),
                "skills_required": career["skills"]
            })

        # Sort by score
        results.sort(key=lambda x: x["match_score"], reverse=True)

        return api_response(True, "Recommendations generated", results)

    except Exception as e:
        return api_response(False, "Recommendation failed", error=str(e), status=500)


# ---------------------------
# TOP CAREERS
# ---------------------------
@career_bp.route("/top", methods=["GET"])
def top_careers():
    try:
        top = sorted(CAREERS, key=lambda x: len(x["skills"]), reverse=True)

        return api_response(True, "Top careers", top[:3])

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# STATS (FOR DASHBOARD)
# ---------------------------
@career_bp.route("/stats", methods=["GET"])
def career_stats():
    try:
        domains = {}

        for c in CAREERS:
            domains[c["domain"]] = domains.get(c["domain"], 0) + 1

        return api_response(True, "Stats", {
            "total_careers": len(CAREERS),
            "domains": domains
        })

    except Exception as e:
        return api_response(False, "Error", error=str(e), status=500)


# ---------------------------
# END (~300 lines)
# ---------------------------