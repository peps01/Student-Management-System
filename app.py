import config
from flask import Flask, render_template, redirect, url_for
from database.sqlite_repo import SqliteRepository
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = config.SECRET_KEY

    if config.DATABASE_TYPE == "sqlite":
        repo = SqliteRepository(config.SQLITE_DB_PATH)
    elif config.DATABASE_TYPE == "mongodb":
        from database.mongo_repo import MongoRepository
        repo = MongoRepository(config.MONGO_URI)
    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {config.DATABASE_TYPE}")

    app.config["repository"] = repo

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login")
    def login():
        return render_template("login.html")

    @app.route("/register")
    def register():
        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
