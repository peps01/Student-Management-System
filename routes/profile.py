from flask import Blueprint, request, jsonify, current_app, session

profile_bp = Blueprint("profile", __name__)


def _get_username(req):
    auth = req.headers.get("X-Username", "")
    return auth or "admin"


@profile_bp.route("/api/profile", methods=["GET"])
def get_profile():
    username = _get_username(request)
    repo = current_app.config["repository"]
    user = repo.get_user(username)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    extra = {}
    if user["role"] == "Student":
        s = repo.get_student_by_username(username)
        if s:
            extra = {"student_id": s["id"], "student_number": s["student_number"],
                     "course_name": s["course_name"], "year": s["year"]}
    elif user["role"] == "Faculty":
        f = repo.get_faculty_by_username(username)
        if f:
            extra = {"faculty_id": f["id"], "department_name": f["department_name"]}

    return jsonify({
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "bio": user["bio"],
        "role": user["role"],
        "joinDate": user["join_date"],
        **extra,
    })


@profile_bp.route("/api/profile", methods=["PUT"])
def update_profile():
    username = _get_username(request)
    data = request.get_json(silent=True)
    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    repo = current_app.config["repository"]
    if repo.update_user(username, data):
        return jsonify({"message": "Profile updated successfully"})
    return jsonify({"error": "Update failed"}), 500


@profile_bp.route("/api/profile/password", methods=["PUT"])
def change_password():
    username = _get_username(request)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    current_pw = data.get("currentPassword", "")
    new_pw = data.get("newPassword", "")

    if len(new_pw) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400
    if new_pw != data.get("confirmPassword", ""):
        return jsonify({"error": "Passwords do not match"}), 400

    repo = current_app.config["repository"]
    if repo.change_password(username, current_pw, new_pw):
        return jsonify({"message": "Password changed successfully"})
    return jsonify({"error": "Current password is incorrect"}), 400
