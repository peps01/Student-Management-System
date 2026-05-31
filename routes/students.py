from flask import Blueprint, request, jsonify, current_app

students_bp = Blueprint("students", __name__)


@students_bp.route("/api/students", methods=["GET"])
def list_students():
    repo = current_app.config["repository"]
    students = repo.list_students()
    return jsonify(students)


@students_bp.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    errors = []
    if not data.get("student_number"): errors.append("Student number is required")
    if not data.get("name"): errors.append("Name is required")
    if not data.get("email"): errors.append("Email is required")
    if not data.get("course_id"): errors.append("Course is required")
    year = data.get("year")
    if not year or not isinstance(year, int) or year < 1 or year > 5:
        errors.append("Year must be between 1 and 5")

    if errors:
        return jsonify({"error": "; ".join(errors)}), 400

    repo = current_app.config["repository"]
    student = repo.add_student(data)
    return jsonify(student), 201


@students_bp.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    year = data.get("year")
    if year and (not isinstance(year, int) or year < 1 or year > 5):
        return jsonify({"error": "Year must be between 1 and 5"}), 400

    repo = current_app.config["repository"]
    if repo.update_student(student_id, data):
        student = repo.get_student(student_id)
        return jsonify(student)
    return jsonify({"error": "Student not found"}), 404


@students_bp.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    repo = current_app.config["repository"]
    if repo.delete_student(student_id):
        return jsonify({"message": "Student deleted successfully"})
    return jsonify({"error": "Student not found"}), 404
