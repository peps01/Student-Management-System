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
    redirect = "/dashboard"
    if role == "Faculty":
        redirect = "/dashboard"
    elif role == "Student":
        redirect = "/dashboard"

    return jsonify({
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "role": role,
        "redirect": redirect,
    })


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get("username", "").strip()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role", "Student").strip()

    if not all([username, name, email, password]):
        return jsonify({"error": "All fields are required"}), 400

    repo = current_app.config["repository"]
    if repo.get_user(username):
        return jsonify({"error": "Username already taken"}), 409

    user = repo.create_user(username, name, email, password, role)
    return jsonify({"message": "Account created successfully", "user": user}), 201
