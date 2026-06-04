from flask import Blueprint, jsonify, current_app

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/dashboard/stats", methods=["GET"])
def dashboard_stats():
    repo = current_app.config["repository"]
    return jsonify(repo.get_dashboard_stats())
