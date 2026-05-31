from flask import Blueprint, request, jsonify, current_app

offerings_bp = Blueprint("offerings", __name__)


@offerings_bp.route("/api/offerings", methods=["GET"])
def list_offerings():
    repo = current_app.config["repository"]
    return jsonify(repo.list_offerings())


@offerings_bp.route("/api/offerings", methods=["POST"])
def add_offering():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    required = ["subject_id", "section", "schedule", "faculty_id", "semester", "school_year"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400
    repo = current_app.config["repository"]
    offering = repo.add_offering(data)
    return jsonify(offering), 201


@offerings_bp.route("/api/offerings/<int:offering_id>", methods=["PUT"])
def update_offering(offering_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    repo = current_app.config["repository"]
    if repo.update_offering(offering_id, data):
        return jsonify({"message": "Offering updated"})
    return jsonify({"error": "Offering not found"}), 404


@offerings_bp.route("/api/offerings/<int:offering_id>", methods=["DELETE"])
def delete_offering(offering_id):
    repo = current_app.config["repository"]
    if repo.delete_offering(offering_id):
        return jsonify({"message": "Offering deleted"})
    return jsonify({"error": "Offering not found"}), 404


@offerings_bp.route("/api/offerings/faculty/<int:faculty_id>", methods=["GET"])
def faculty_offerings(faculty_id):
    repo = current_app.config["repository"]
    return jsonify(repo.get_faculty_offerings(faculty_id))
