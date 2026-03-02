import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO

from .config import config_map
from .routes.alerts import alerts_bp
from .routes.analytics import analytics_bp
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.health import health_bp
from .routes.irrigation import irrigation_bp
from .routes.predict import predict_bp
from .utils.db import init_db
from .utils.response import error_response

socketio = SocketIO(cors_allowed_origins="*")

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

    # Ensure SQLite schema exists before any API requests hit service queries.
    init_db()
    
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

    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(alerts_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(irrigation_bp, url_prefix="/api")
    
    socketio.init_app(app)
    
    print("App factory initialized successfully")
    return app
