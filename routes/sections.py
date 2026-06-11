from flask import Blueprint, request, jsonify, current_app
from routes.auth import require_role

sections_bp = Blueprint("sections", __name__)


@sections_bp.route("/api/sections", methods=["GET"])
@require_role("Administrator")
def list_sections():
    repo = current_app.config["repository"]
    return jsonify(repo.list_sections())


@sections_bp.route("/api/sections", methods=["POST"])
@require_role("Administrator")
def add_section():
    data = request.get_json(silent=True)
    if not data or not data.get("name", "").strip():
        return jsonify({"error": "Section name is required"}), 400
    repo = current_app.config["repository"]
    section = repo.add_section({"name": data["name"].strip()})
    return jsonify(section), 201


@sections_bp.route("/api/sections/<int:section_id>", methods=["PUT"])
@require_role("Administrator")
def update_section(section_id):
    data = request.get_json(silent=True)
    if not data or not data.get("name", "").strip():
        return jsonify({"error": "Section name is required"}), 400
    repo = current_app.config["repository"]
    if repo.update_section(section_id, {"name": data["name"].strip()}):
        return jsonify({"message": "Section updated"})
    return jsonify({"error": "Section not found"}), 404


@sections_bp.route("/api/sections/<int:section_id>", methods=["DELETE"])
@require_role("Administrator")
def delete_section(section_id):
    repo = current_app.config["repository"]
    if repo.delete_section(section_id):
        return jsonify({"message": "Section deleted"})
    return jsonify({"error": "Section not found"}), 404
