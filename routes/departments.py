from flask import Blueprint, request, jsonify, current_app

departments_bp = Blueprint("departments", __name__)


@departments_bp.route("/api/departments", methods=["GET"])
def list_departments():
    repo = current_app.config["repository"]
    return jsonify(repo.list_departments())


@departments_bp.route("/api/departments", methods=["POST"])
def add_department():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    if not data.get("name") or not data.get("code"):
        return jsonify({"error": "Name and code are required"}), 400
    repo = current_app.config["repository"]
    dept = repo.add_department(data)
    return jsonify(dept), 201


@departments_bp.route("/api/departments/<int:dept_id>", methods=["PUT"])
def update_department(dept_id):
    data = request.get_json(silent=True)
    if not data or not data.get("name") or not data.get("code"):
        return jsonify({"error": "Name and code are required"}), 400
    repo = current_app.config["repository"]
    if repo.update_department(dept_id, data):
        return jsonify({"message": "Department updated"})
    return jsonify({"error": "Department not found"}), 404


@departments_bp.route("/api/departments/<int:dept_id>", methods=["DELETE"])
def delete_department(dept_id):
    repo = current_app.config["repository"]
    if repo.delete_department(dept_id):
        return jsonify({"message": "Department deleted"})
    return jsonify({"error": "Department not found"}), 404
