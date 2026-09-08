"""Environment-driven prototype configuration."""
import os
from dataclasses import dataclass, field
from pathlib import Path


def _origins():
    return [x.strip() for x in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",") if x.strip()]


@dataclass
class Settings:
    app_name: str = "Pneumatic Cylinder Digital Twin API"
    version: str = "2.1.0"
    database_path: Path = field(default_factory=lambda: Path(os.getenv("DATABASE_PATH", "data/predictions.db")))
    classifier_path: Path = field(default_factory=lambda: Path(os.getenv("CLASSIFIER_PATH", "models/fault_classifier_v2_1.joblib")))
    health_model_path: Path = field(default_factory=lambda: Path(os.getenv("HEALTH_MODEL_PATH", "models/health_estimator_v2_1.joblib")))
    classifier_metrics_path: Path = Path("models/fault_classifier_v2_1_metrics.json")
    classifier_cv_metrics_path: Path = Path("models/fault_classifier_v2_1_cv_metrics.json")
    health_metrics_path: Path = Path("models/health_estimator_v2_1_metrics.json")
    cors_origins: list[str] = field(default_factory=_origins)
    buffer_size: int = field(default_factory=lambda: int(os.getenv("FEATURE_BUFFER_SIZE", "100")))
    critical_health: float = field(default_factory=lambda: float(os.getenv("CRITICAL_HEALTH", "30")))
    max_rul_cycles: int = field(default_factory=lambda: int(os.getenv("MAX_RUL_CYCLES", "10000")))
    websocket_interval: float = field(default_factory=lambda: float(os.getenv("WEBSOCKET_INTERVAL", "1.0")))


settings = Settings()
