import os

class Config:
    """Base configuration."""
    APP_NAME = os.getenv("APP_NAME", "agroguard-ai-backend")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secure-key-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "default-jwt-key"))
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    
    MODEL_DIR = os.getenv("MODEL_DIR", "models")
    DISEASE_MODEL_PATH = os.getenv("DISEASE_MODEL_PATH", os.path.join(MODEL_DIR, "disease_model.h5"))
    DISEASE_LABELS_PATH = os.getenv("DISEASE_LABELS_PATH", os.path.join(MODEL_DIR, "disease_labels.json"))
    IRRIGATION_MODEL_PATH = os.getenv(
        "IRRIGATION_MODEL_PATH", os.path.join(MODEL_DIR, "irrigation_model.pkl")
    )

    WEATHER_API_BASE_URL = os.getenv("WEATHER_API_BASE_URL", "https://api.open-meteo.com/v1/forecast")
    WEATHER_TIMEOUT_SECONDS = float(os.getenv("WEATHER_TIMEOUT_SECONDS", "5"))

    # Database Configuration
    _database_url = os.getenv("DATABASE_URL", "sqlite:///data/sensor_readings.db")
    if _database_url and _database_url.startswith("postgres://"):
        _database_url = _database_url.replace("postgres://", "postgresql://", 1)
    
    DATABASE_URL = _database_url
    SQLALCHEMY_DATABASE_URI = _database_url
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
