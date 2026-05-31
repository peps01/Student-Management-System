import config
from flask import Flask, render_template, redirect, url_for
from database.sqlite_repo import SqliteRepository
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.students import students_bp
from routes.grades import grades_bp
from routes.attendance import attendance_bp
from routes.announcements import announcements_bp
from routes.departments import departments_bp
from routes.courses import courses_bp
from routes.subjects import subjects_bp
from routes.faculties import faculties_bp
from routes.class_offerings import offerings_bp
from routes.enrollments import enrollments_bp
from routes.reports import reports_bp


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
    app.register_blueprint(departments_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(faculties_bp)
    app.register_blueprint(offerings_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login")
    def login():
        return render_template("login.html")

    # Admin pages
    @app.route("/admin/dashboard")
    def admin_dashboard():
        return render_template("admin_dashboard.html")

    @app.route("/admin/departments")
    def admin_departments():
        return render_template("departments.html")

    @app.route("/admin/courses")
    def admin_courses():
        return render_template("courses.html")

    @app.route("/admin/subjects")
    def admin_subjects():
        return render_template("subjects.html")

    @app.route("/admin/faculties")
    def admin_faculties():
        return render_template("faculties.html")

    @app.route("/admin/offerings")
    def admin_offerings():
        return render_template("offerings.html")

    @app.route("/admin/enrollments")
    def admin_enrollments():
        return render_template("enrollments.html")

    @app.route("/admin/reports")
    def admin_reports():
        return render_template("reports.html")

    @app.route("/admin/students")
    def admin_students():
        return render_template("students.html")

    @app.route("/admin/grades")
    def admin_grades():
        return render_template("grades.html")

    @app.route("/admin/attendance")
    def admin_attendance():
        return render_template("attendance.html")

    @app.route("/admin/announcements")
    def admin_announcements():
        return render_template("announcements.html")

    # Faculty pages
    @app.route("/faculty/dashboard")
    def faculty_dashboard():
        return render_template("faculty_dashboard.html")

    @app.route("/faculty/classes")
    def faculty_classes():
        return render_template("faculty_classes.html")

    @app.route("/faculty/attendance/<int:offering_id>")
    def faculty_attendance(offering_id):
        return render_template("faculty_attendance.html", offering_id=offering_id)

    @app.route("/faculty/grades/<int:offering_id>")
    def faculty_grades(offering_id):
        return render_template("faculty_grades.html", offering_id=offering_id)

    # Student pages
    @app.route("/student/dashboard")
    def student_dashboard():
        return render_template("student_dashboard.html")

    @app.route("/student/enrollment")
    def student_enrollment():
        return render_template("student_enrollment.html")

    @app.route("/student/grades")
    def student_grades():
        return render_template("student_grades.html")

    @app.route("/student/attendance")
    def student_attendance():
        return render_template("student_attendance.html")

    # Profile (shared)
    @app.route("/profile")
    def profile():
        return render_template("profile.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
