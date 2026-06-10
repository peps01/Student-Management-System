import uuid
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, jsonify, current_app, g
from werkzeug.security import check_password_hash

auth_bp = Blueprint("auth", __name__)

_tokens = {}


def _generate_token(username: str, role: str) -> str:
    token = str(uuid.uuid4())
    _tokens[token] = {
        "username": username,
        "role": role,
        "created_at": datetime.utcnow(),
    }
    return token


def _validate_token(token: str):
    data = _tokens.get(token)
    if not data:
        return None, None
    if datetime.utcnow() - data["created_at"] > timedelta(hours=24):
        del _tokens[token]
        return None, None
    return data["username"], data["role"]


def _invalidate_token(token: str):
    _tokens.pop(token, None)


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401
        token = auth_header.split(" ", 1)[1]
        username, role = _validate_token(token)
        if username is None:
            return jsonify({"error": "Invalid or expired token"}), 401
        g.username = username
        g.role = role
        return f(*args, **kwargs)
    return decorated


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"error": "Authentication required"}), 401
            token = auth_header.split(" ", 1)[1]
            username, role = _validate_token(token)
            if username is None:
                return jsonify({"error": "Invalid or expired token"}), 401
            g.username = username
            g.role = role
            if role not in roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    repo = current_app.config["repository"]
    user = repo.get_user(username)
    if user is None or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    role = user["role"]
    redirect = "/admin/dashboard"
    if role == "Faculty":
        redirect = "/faculty/dashboard"
    elif role == "Student":
        redirect = "/student/dashboard"

    token = _generate_token(username, role)

    return jsonify({
        "token": token,
        "username": user["username"],
        "name": user["name"],
        "email": user["email"],
        "role": role,
        "redirect": redirect,
    })


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        _invalidate_token(auth_header.split(" ", 1)[1])
    return jsonify({"message": "Logged out successfully"})
