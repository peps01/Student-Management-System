from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_auth, require_role

faculties_bp = Blueprint("faculties", __name__)


@faculties_bp.route("/api/faculties", methods=["GET"])
@require_auth
def list_faculties():
    repo = current_app.config["repository"]
    return jsonify(repo.list_faculties())


@faculties_bp.route("/api/faculties", methods=["POST"])
@require_role("Administrator")
def add_faculty():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    if not data.get("name") or not data.get("email") or not data.get("department_id"):
        return jsonify({"error": "Name, email, and department_id are required"}), 400
    if not data.get("username"):
        data["username"] = data["email"].split("@")[0].lower()
    repo = current_app.config["repository"]
    faculty = repo.add_faculty(data)
    return jsonify(faculty), 201


@faculties_bp.route("/api/faculties/<int:faculty_id>", methods=["PUT"])
@require_role("Administrator")
def update_faculty(faculty_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    repo = current_app.config["repository"]
    if repo.update_faculty(faculty_id, data):
        return jsonify({"message": "Faculty updated"})
    return jsonify({"error": "Faculty not found"}), 404


@faculties_bp.route("/api/faculties/<int:faculty_id>", methods=["DELETE"])
@require_role("Administrator")
def delete_faculty(faculty_id):
    repo = current_app.config["repository"]
    if repo.delete_faculty(faculty_id):
        return jsonify({"message": "Faculty deleted"})
    return jsonify({"error": "Faculty not found"}), 404
