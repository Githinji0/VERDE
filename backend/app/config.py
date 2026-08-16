import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "VERDE"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    SECRET_KEY: str = "verde_super_secret_key_change_in_production_32bytes!"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./verde.db"

    # BRAIN Client
    BRAIN_API_BASE_URL: str = "https://api.worldquantbrain.com"
    BRAIN_DEBUG: bool = False
    BRAIN_TIMEOUT: int = 60
    BRAIN_MAX_RETRIES: int = 3

    # Validation Target Thresholds (Configurable defaults)
    MIN_SHARPE: float = 1.25
    MIN_FITNESS: float = 1.00
    MAX_TURNOVER: float = 0.70
    MIN_MARGIN_BPS: float = 4.00

    # Near Miss Thresholds (Configurable defaults)
    NEAR_MISS_MIN_SHARPE: float = 1.10
    NEAR_MISS_MAX_SHARPE: float = 1.24
    NEAR_MISS_MIN_FITNESS: float = 0.85
    NEAR_MISS_MAX_FITNESS: float = 0.99

    # Research Score Weights (Sum = 1.0)
    WEIGHT_SHARPE: float = 0.30
    WEIGHT_FITNESS: float = 0.25
    WEIGHT_TURNOVER: float = 0.15
    WEIGHT_STABILITY: float = 0.10
    WEIGHT_ROBUSTNESS: float = 0.10
    WEIGHT_DIVERSITY: float = 0.05
    WEIGHT_SIMPLICITY: float = 0.05

    # Priority Allocation
    PROVEN_RATIO: float = 0.70
    EXPLORED_RATIO: float = 0.20
    NOVEL_RATIO: float = 0.10

    # Preflight Thresholds
    PREFLIGHT_MIN_VALID_RATIO: float = 0.80
    PREFLIGHT_MIN_UNIQUE_VALUES: int = 10
    PREFLIGHT_MIN_CROSS_SECTIONAL_STD: float = 0.0001
    PREFLIGHT_CONSTANT_TOLERANCE: float = 0.95

    # AI Integration (Optional)
    AI_ENABLED: bool = False
    AI_PROVIDER: str = "none"
    AI_ENCRYPTION_KEY: str = "verde_master_secret_encryption_key_32_bytes!!"


settings = Settings()
