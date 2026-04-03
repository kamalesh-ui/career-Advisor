# app.py

from flask import Flask, jsonify, request, send_from_directory, g
from flask_cors import CORS
import logging
import os
import time

# DB import (single instance)
from models.user_model import db

# ---------------------------
# APP FACTORY
# ---------------------------
def create_app():
    app = Flask(
        __name__,
        static_folder="frontend/build",
        template_folder="frontend/build"
    )

    # ---------------------------
    # CONFIGURATION
    # ---------------------------
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "dev-secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL", "sqlite:///app.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ---------------------------
    # EXTENSIONS
    # ---------------------------
    db.init_app(app)
    CORS(app)

    # ---------------------------
    # LOGGING SETUP
    # ---------------------------
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger("career_app")

    # ---------------------------
    # REQUEST MIDDLEWARE
    # ---------------------------
    @app.before_request
    def start_timer():
        g.start_time = time.time()

    @app.after_request
    def log_request(response):
        duration = round(time.time() - g.start_time, 4)

        logger.info(
            f"{request.method} {request.path} "
            f"Status:{response.status_code} "
            f"Time:{duration}s"
        )

        return response

    # ---------------------------
    # IMPORT BLUEPRINTS
    # ---------------------------
    from controllers.user_controller import user_bp
    from controllers.career_controller import career_bp
    from controllers.roadmap_controller import roadmap_bp
    from controllers.chatbot_controller import chatbot_bp
    from controllers.feedback_controller import feedback_bp

    # ---------------------------
    # REGISTER BLUEPRINTS
    # ---------------------------
    app.register_blueprint(user_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(feedback_bp)

    # ---------------------------
    # STANDARD RESPONSE HELPER
    # ---------------------------
    def api_response(success=True, message="", data=None, error=None):
        return jsonify({
            "success": success,
            "message": message,
            "data": data,
            "error": error
        })

    # ---------------------------
    # HEALTH CHECK
    # ---------------------------
    @app.route("/api/health")
    def health():
        return api_response(True, "Backend is running 🚀")

    # ---------------------------
    # API DOCUMENTATION
    # ---------------------------
    @app.route("/api/docs")
    def docs():
        return jsonify({
            "name": "Career Advisor API",
            "version": "1.0",
            "endpoints": {
                "auth": [
                    "/api/users/register",
                    "/api/users/login"
                ],
                "career": [
                    "/api/careers",
                    "/api/roadmap"
                ],
                "chatbot": [
                    "/api/chatbot"
                ]
            }
        })

    # ---------------------------
    # TEST ROUTES
    # ---------------------------
    @app.route("/api/test")
    def test():
        return api_response(True, "Test route working")

    # ---------------------------
    # FRONTEND SERVING
    # ---------------------------
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, "index.html")

    # ---------------------------
    # ERROR HANDLERS
    # ---------------------------
    @app.errorhandler(400)
    def bad_request(e):
        return api_response(False, "Bad request", error=str(e)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return api_response(False, "Unauthorized", error=str(e)), 401

    @app.errorhandler(403)
    def forbidden(e):
        return api_response(False, "Forbidden", error=str(e)), 403

    @app.errorhandler(404)
    def not_found(e):
        return api_response(False, "Route not found"), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server Error: {str(e)}")
        return api_response(False, "Internal server error"), 500

    @app.errorhandler(Exception)
    def global_error(e):
        logger.error(f"Unhandled Error: {str(e)}")
        return api_response(False, "Unexpected error", error=str(e)), 500

    # ---------------------------
    # CLI COMMANDS
    # ---------------------------
    @app.cli.command("init-db")
    def init_db():
        with app.app_context():
            db.create_all()
            print("✅ Database initialized")

    @app.cli.command("drop-db")
    def drop_db():
        with app.app_context():
            db.drop_all()
            print("⚠️ Database dropped")

    @app.cli.command("seed-db")
    def seed_db():
        from models.user_model import User

        with app.app_context():
            user = User(
                email="admin@test.com",
                password="123456",
                name="Admin"
            )
            db.session.add(user)
            db.session.commit()
            print("🌱 Database seeded")

    # ---------------------------
    # APP STARTUP LOG
    # ---------------------------
    @app.before_first_request
    def startup_message():
        logger.info("🚀 Server started successfully")

    return app


# ---------------------------
# MAIN ENTRY
# ---------------------------
if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        db.create_all()

    print("🔥 Career Advisor Backend Running...")
    print("🌐 http://127.0.0.1:5000")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )