from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_role, require_auth

grades_bp = Blueprint("grades", __name__)


@grades_bp.route("/api/grades", methods=["GET"])
@require_role("Administrator", "Faculty")
def list_grades():
    offering_id = request.args.get("offering_id", type=int)
    repo = current_app.config["repository"]
    if offering_id:
        grades = repo.list_grades(offering_id)
    else:
        grades = []
    return jsonify(grades)


@grades_bp.route("/api/grades/<int:offering_id>/<int:student_id>", methods=["PUT"])
@require_role("Administrator", "Faculty")
def upsert_grade(offering_id, student_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    for field in ("prelim", "midterm", "final"):
        val = data.get(field, 0)
        if not isinstance(val, (int, float)) or val < 0 or val > 100:
            return jsonify({"error": f"{field} must be between 0 and 100"}), 400
    repo = current_app.config["repository"]
    grade = repo.upsert_grade(offering_id, student_id, data)
    return jsonify(grade)


@grades_bp.route("/api/grades/student/<int:student_id>", methods=["GET"])
@require_auth
def get_student_grades(student_id):
    repo = current_app.config["repository"]
    grades = repo.get_student_grades(student_id)
    return jsonify(grades)
