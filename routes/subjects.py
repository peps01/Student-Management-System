from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_auth, require_role

subjects_bp = Blueprint("subjects", __name__)


@subjects_bp.route("/api/subjects", methods=["GET"])
@require_auth
def list_subjects():
    repo = current_app.config["repository"]
    return jsonify(repo.list_subjects())


@subjects_bp.route("/api/subjects", methods=["POST"])
@require_role("Administrator")
def add_subject():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    if not data.get("name") or not data.get("code") or not data.get("course_id"):
        return jsonify({"error": "Name, code, and course_id are required"}), 400
    repo = current_app.config["repository"]
    subject = repo.add_subject(data)
    return jsonify(subject), 201


@subjects_bp.route("/api/subjects/<int:subject_id>", methods=["PUT"])
@require_role("Administrator")
def update_subject(subject_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    repo = current_app.config["repository"]
    if repo.update_subject(subject_id, data):
        return jsonify({"message": "Subject updated"})
    return jsonify({"error": "Subject not found"}), 404


@subjects_bp.route("/api/subjects/<int:subject_id>", methods=["DELETE"])
@require_role("Administrator")
def delete_subject(subject_id):
    repo = current_app.config["repository"]
    if repo.delete_subject(subject_id):
        return jsonify({"message": "Subject deleted"})
    return jsonify({"error": "Subject not found"}), 404
