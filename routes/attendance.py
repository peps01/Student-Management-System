from flask import Blueprint, jsonify, current_app

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/attendance", methods=["GET"])
def list_attendance():
    repo = current_app.config["repository"]
    records = repo.list_attendance()
    return jsonify(records)


@attendance_bp.route("/api/attendance/<int:student_id>/<int:day_index>", methods=["PUT"])
def toggle_attendance(student_id, day_index):
    if day_index < 0 or day_index > 4:
        return jsonify({"error": "day_index must be between 0 and 4"}), 400

    repo = current_app.config["repository"]
    if repo.toggle_attendance(student_id, day_index):
        return jsonify({"message": "Attendance toggled successfully"})
    return jsonify({"error": "Student not found"}), 404
