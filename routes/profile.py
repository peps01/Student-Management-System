from flask import Blueprint, request, jsonify, current_app

profile_bp = Blueprint("profile", __name__)
USERNAME = "admin"


@profile_bp.route("/api/profile", methods=["GET"])
def get_profile():
    repo = current_app.config["repository"]
    user = repo.get_user(USERNAME)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "bio": user["bio"],
        "role": user["role"],
        "joinDate": user["join_date"],
    })


@profile_bp.route("/api/profile", methods=["PUT"])
def update_profile():
    data = request.get_json(silent=True)
    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email are required"}), 400

    repo = current_app.config["repository"]
    if repo.update_user(USERNAME, data):
        return jsonify({"message": "Profile updated successfully"})
    return jsonify({"error": "Update failed"}), 500


@profile_bp.route("/api/profile/password", methods=["PUT"])
def change_password():
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
    if repo.change_password(USERNAME, current_pw, new_pw):
        return jsonify({"message": "Password changed successfully"})
    return jsonify({"error": "Current password is incorrect"}), 400
