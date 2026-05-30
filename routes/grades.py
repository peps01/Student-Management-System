from flask import Blueprint, request, jsonify, current_app

grades_bp = Blueprint("grades", __name__)

VALID_SUBJECTS = {"Math", "English", "Science", "History", "PE"}


@grades_bp.route("/api/grades", methods=["GET"])
def list_grades():
    repo = current_app.config["repository"]
    grades = repo.list_grades()
    return jsonify(grades)


@grades_bp.route("/api/grades/<int:student_id>", methods=["PUT"])
def update_grade(student_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    subject = data.get("subject", "")
    score = data.get("score")

    if subject not in VALID_SUBJECTS:
        return jsonify({"error": f"Invalid subject. Valid: {', '.join(sorted(VALID_SUBJECTS))}"}), 400
    if not isinstance(score, (int, float)) or score < 0 or score > 100:
        return jsonify({"error": "Score must be a number between 0 and 100"}), 400

    repo = current_app.config["repository"]
    if repo.update_grade(student_id, subject, score):
        return jsonify({"message": "Grade updated successfully"})
    return jsonify({"error": "Student not found"}), 404
