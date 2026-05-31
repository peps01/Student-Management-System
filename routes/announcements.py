from flask import Blueprint, request, jsonify, current_app

announcements_bp = Blueprint("announcements", __name__)


@announcements_bp.route("/api/announcements", methods=["GET"])
def list_announcements():
    repo = current_app.config["repository"]
    announcements = repo.list_announcements()
    return jsonify(announcements)


@announcements_bp.route("/api/announcements", methods=["POST"])
def add_announcement():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    title = data.get("title", "").strip()
    body = data.get("body", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not body:
        return jsonify({"error": "Body is required"}), 400

    repo = current_app.config["repository"]
    annc = repo.add_announcement(data)
    return jsonify(annc), 201
