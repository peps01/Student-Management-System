import config
from flask import Flask, render_template, redirect, url_for
from database.sqlite_repo import SqliteRepository
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.students import students_bp
from routes.grades import grades_bp
from routes.attendance import attendance_bp
from routes.announcements import announcements_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    if config.DATABASE_TYPE == "sqlite":
        repo = SqliteRepository(config.SQLITE_DB_PATH)
    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {config.DATABASE_TYPE}")

    app.config["repository"] = repo

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(grades_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(announcements_bp)

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/students")
    def students():
        return render_template("students.html")

    @app.route("/grades")
    def grades():
        return render_template("grades.html")

    @app.route("/attendance")
    def attendance():
        return render_template("attendance.html")

    @app.route("/announcements")
    def announcements():
        return render_template("announcements.html")

    @app.route("/profile")
    def profile():
        return render_template("profile.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
