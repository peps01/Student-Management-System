from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_role, require_auth

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/attendance", methods=["GET"])
@require_role("Administrator", "Faculty")
def list_attendance():
    offering_id = request.args.get("offering_id", type=int)
    if not offering_id:
        return jsonify({"error": "offering_id is required"}), 400
    repo = current_app.config["repository"]
    records = repo.list_attendance(offering_id)
    return jsonify(records)


@attendance_bp.route("/api/attendance/mark", methods=["POST"])
@require_role("Administrator", "Faculty")
def mark_attendance():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    offering_id = data.get("offering_id")
    student_id = data.get("student_id")
    date = data.get("date")
    status = data.get("status", "Present")
    if not all([offering_id, student_id, date]):
        return jsonify({"error": "offering_id, student_id, and date are required"}), 400
    repo = current_app.config["repository"]
    result = repo.mark_attendance(offering_id, student_id, date, status)
    return jsonify(result)


@attendance_bp.route("/api/attendance/summary/<int:student_id>", methods=["GET"])
@require_auth
def attendance_summary(student_id):
    repo = current_app.config["repository"]
    summary = repo.get_student_attendance_summary(student_id)
    return jsonify(summary)
