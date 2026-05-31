from flask import Blueprint, request, jsonify, current_app

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    repo = current_app.config["repository"]
    user = repo.get_user(username)
    if user is None or user["password"] != password:
        return jsonify({"error": "Invalid username or password"}), 401

    role = user["role"]
    redirect = "/admin/dashboard"
    if role == "Faculty":
        redirect = "/faculty/dashboard"
    elif role == "Student":
        redirect = "/student/dashboard"

    return jsonify({
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "role": role,
        "redirect": redirect,
    })
