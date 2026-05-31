from flask import Blueprint, request, jsonify, current_app

enrollments_bp = Blueprint("enrollments", __name__)


@enrollments_bp.route("/api/enrollments", methods=["GET"])
def list_enrollments():
    status = request.args.get("status")
    repo = current_app.config["repository"]
    return jsonify(repo.list_enrollments(status))


@enrollments_bp.route("/api/enrollments", methods=["POST"])
def create_enrollment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    student_id = data.get("student_id")
    offering_ids = data.get("offering_ids", [])
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400
    if not offering_ids or not isinstance(offering_ids, list):
        return jsonify({"error": "offering_ids must be a non-empty list"}), 400
    repo = current_app.config["repository"]
    enrollment = repo.create_enrollment(student_id, offering_ids)
    return jsonify(enrollment), 201


@enrollments_bp.route("/api/enrollments/<int:enrollment_id>/approve", methods=["PUT"])
def approve_enrollment(enrollment_id):
    repo = current_app.config["repository"]
    if repo.approve_enrollment(enrollment_id):
        return jsonify({"message": "Enrollment approved"})
    return jsonify({"error": "Enrollment not found or already processed"}), 404


@enrollments_bp.route("/api/enrollments/<int:enrollment_id>/reject", methods=["PUT"])
def reject_enrollment(enrollment_id):
    repo = current_app.config["repository"]
    if repo.reject_enrollment(enrollment_id):
        return jsonify({"message": "Enrollment rejected"})
    return jsonify({"error": "Enrollment not found or already processed"}), 404


@enrollments_bp.route("/api/enrollments/student/<int:student_id>", methods=["GET"])
def student_enrollments(student_id):
    repo = current_app.config["repository"]
    return jsonify(repo.get_student_enrollments(student_id))
