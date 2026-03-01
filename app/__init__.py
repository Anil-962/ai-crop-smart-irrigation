import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from app.config import config_map
from app.routes.auth import auth_bp
from app.routes.decision import decision_bp
from app.routes.health import health_bp
from app.routes.predict import predict_bp
from app.routes.dashboard import dashboard_bp
from app.routes.analytics import analytics_bp
from app.routes.irrigation import irrigation_bp
from app.routes.alerts import alerts_bp
from app.utils.response import error_response

socketio = SocketIO(cors_allowed_origins="*", async_mode="gevent")

def setup_logging(app):
    """Configure logging for the application."""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/agroguard.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('AgroGuard startup')

def create_app() -> Flask:
    env = os.getenv("FLASK_ENV", "default")
    config_class = config_map.get(env, config_map["default"])
    
    app = Flask(__name__)
    
    app.config.from_object(config_class)
    
    if not app.debug:
        setup_logging(app)
        
        # Log warnings for missing critical production settings
        if not os.getenv("DATABASE_URL"):
            app.logger.warning("DATABASE_URL not found. Falling back to SQLite.")
        if os.getenv("SECRET_KEY", "default-secure-key-change-me") == "default-secure-key-change-me":
            app.logger.warning("SECRET_KEY is using the default value. Please set a secure SECRET_KEY in production.")
        if os.getenv("JWT_SECRET_KEY", "default-jwt-key") == "default-jwt-key":
             app.logger.warning("JWT_SECRET_KEY is using the default value. Please set a secure JWT_SECRET_KEY in production.")
    
    # Enable CORS for specified origins
    CORS(app, resources={r"/*": {"origins": app.config['CORS_ORIGINS']}}, supports_credentials=True)
    
    # Global exception handlers
    @app.errorhandler(400)
    def bad_request(e):
        return error_response(str(e) if e.description is None else e.description, 400)

    @app.errorhandler(404)
    def not_found(e):
        return error_response("Endpoint not found", 404)
        
    @app.errorhandler(405)
    def method_not_allowed(e):
        return error_response("Method not allowed", 405)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal Server Error: {str(e)}")
        return error_response("Internal server error", 500)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    try:
        from app.utils.db import init_db
        init_db()
    except Exception as e:
        print(f"CRITICAL ERROR: Database initialization failed: {e}")
        app.logger.critical(f"Database initialization failed: {e}")
    
    socketio.init_app(app)
    
    from app.routes.zones import zones_bp
    from app.routes.sensors import sensors_bp
    
    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(predict_bp, url_prefix="/api/predict")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
    app.register_blueprint(decision_bp, url_prefix="/api/decision")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(irrigation_bp, url_prefix="/api/irrigation")
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
    app.register_blueprint(zones_bp, url_prefix="/api/zones")
    app.register_blueprint(sensors_bp, url_prefix="/api/sensors")
    
    @app.route("/<path:path>")
    def serve_spa(path):
        if path.startswith("api/"):
            return error_response("Endpoint not found", 404)
        return render_template("index.html")

    print("App factory initialized successfully")
    return app
