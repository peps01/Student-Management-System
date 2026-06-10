from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_auth, require_role

enrollments_bp = Blueprint("enrollments", __name__)


@enrollments_bp.route("/api/enrollments", methods=["GET"])
@require_role("Administrator")
def list_enrollments():
    status = request.args.get("status")
    repo = current_app.config["repository"]
    return jsonify(repo.list_enrollments(status))


@enrollments_bp.route("/api/enrollments", methods=["POST"])
@require_auth
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

    # Validate student's course matches each offering's subject course
    student = repo.get_student(student_id)
    if student is None:
        return jsonify({"error": "Student not found"}), 404
    student_course = student.get("course_id")
    bad_ids = []
    for oid in offering_ids:
        offering = repo.get_offering(oid)
        if offering is None:
            bad_ids.append(oid)
            continue
        if offering.get("course_id") != student_course:
            bad_ids.append(oid)
    if bad_ids:
        return jsonify({
            "error": "Some offerings do not belong to your course",
            "invalid_offering_ids": bad_ids
        }), 400

    enrollment = repo.create_enrollment(student_id, offering_ids)
    return jsonify(enrollment), 201


@enrollments_bp.route("/api/enrollments/<int:enrollment_id>/approve", methods=["PUT"])
@require_role("Administrator")
def approve_enrollment(enrollment_id):
    repo = current_app.config["repository"]
    if repo.approve_enrollment(enrollment_id):
        return jsonify({"message": "Enrollment approved"})
    return jsonify({"error": "Enrollment not found or already processed"}), 404


@enrollments_bp.route("/api/enrollments/<int:enrollment_id>/reject", methods=["PUT"])
@require_role("Administrator")
def reject_enrollment(enrollment_id):
    repo = current_app.config["repository"]
    if repo.reject_enrollment(enrollment_id):
        return jsonify({"message": "Enrollment rejected"})
    return jsonify({"error": "Enrollment not found or already processed"}), 404


@enrollments_bp.route("/api/enrollments/student/<int:student_id>", methods=["GET"])
@require_auth
def student_enrollments(student_id):
    repo = current_app.config["repository"]
    return jsonify(repo.get_student_enrollments(student_id))
