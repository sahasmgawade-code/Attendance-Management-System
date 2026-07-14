import os
from flask import Flask
from dotenv import load_dotenv
from routes.attendance import attendance_bp
from config.config import Config
from routes.home import home_bp
from routes.reports import reports_bp
from routes.edit_attendance import edit_bp
from routes.past_attendance import past_bp
from routes.checkin import checkin_bp
from routes.auth import auth_bp
from datetime import timedelta
load_dotenv()
def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-key")

    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("RENDER"))

    settings = Config.load_settings()

    app.config["SETTINGS"] = settings

    app.register_blueprint(home_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(edit_bp)
    app.register_blueprint(past_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(auth_bp)
    return app


app = create_app()


if __name__ == "__main__":
    settings = Config.load_settings()
    app.run(
        debug=settings.get("debug", False),
        host="0.0.0.0",
        use_reloader=False,
        port=5000
    )