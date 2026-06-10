from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_role

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/api/dashboard/stats", methods=["GET"])
@require_role("Administrator")
def dashboard_stats():
    repo = current_app.config["repository"]
    return jsonify(repo.get_dashboard_stats())


@reports_bp.route("/api/reports/enrollment", methods=["GET"])
@require_role("Administrator")
def enrollment_report():
    repo = current_app.config["repository"]
    return jsonify(repo.get_enrollment_report())


@reports_bp.route("/api/reports/attendance", methods=["GET"])
@require_role("Administrator")
def attendance_report():
    offering_id = request.args.get("offering_id", type=int)
    if not offering_id:
        return jsonify({"error": "offering_id is required"}), 400
    repo = current_app.config["repository"]
    return jsonify(repo.get_attendance_report(offering_id))


@reports_bp.route("/api/reports/grades", methods=["GET"])
@require_role("Administrator")
def grade_report():
    offering_id = request.args.get("offering_id", type=int)
    if not offering_id:
        return jsonify({"error": "offering_id is required"}), 400
    repo = current_app.config["repository"]
    return jsonify(repo.get_grade_report(offering_id))


@reports_bp.route("/api/reports/export/<report_type>/<int:offering_id>", methods=["GET"])
@require_role("Administrator")
def export_report(report_type, offering_id):
    repo = current_app.config["repository"]
    if report_type == "attendance":
        data = repo.get_attendance_report(offering_id)
    elif report_type == "grades":
        data = repo.get_grade_report(offering_id)
    else:
        return jsonify({"error": "Invalid report type"}), 400
    return jsonify(data)
