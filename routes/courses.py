from flask import Blueprint, request, jsonify, current_app

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("/api/courses", methods=["GET"])
def list_courses():
    repo = current_app.config["repository"]
    return jsonify(repo.list_courses())


@courses_bp.route("/api/courses", methods=["POST"])
def add_course():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    if not data.get("name") or not data.get("code") or not data.get("department_id"):
        return jsonify({"error": "Name, code, and department_id are required"}), 400
    repo = current_app.config["repository"]
    course = repo.add_course(data)
    return jsonify(course), 201


@courses_bp.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    repo = current_app.config["repository"]
    if repo.update_course(course_id, data):
        return jsonify({"message": "Course updated"})
    return jsonify({"error": "Course not found"}), 404


@courses_bp.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    repo = current_app.config["repository"]
    if repo.delete_course(course_id):
        return jsonify({"message": "Course deleted"})
    return jsonify({"error": "Course not found"}), 404
