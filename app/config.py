from functools import lru_cache

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception as e:  # pragma: no cover - environment/import guard
    raise ImportError(
        "pydantic is required to load application settings. Install it with:\n"
        "    pip install pydantic\n"
        "Original error: %s" % e
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "VIGIL"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Database
    DATABASE_URL: str = ""
    ASYNC_DATABASE_URL: str = ""

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Auth
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Screening weights — must sum to 100
    WEIGHT_NAME: int = 25
    WEIGHT_DOB: int = 15
    WEIGHT_ID: int = 20
    WEIGHT_NATIONALITY: int = 10
    WEIGHT_OCCUPATION: int = 5
    WEIGHT_ADVERSE_MEDIA: int = 10
    WEIGHT_PEP: int = 15

    # Thresholds
    FUZZY_NAME_THRESHOLD: int = 85
    SCORE_HIGH_THRESHOLD: int = 50
    TOTAL_WEIGHT: int = 100

    # External APIs
    NEWS_API_KEY: str = ""
    GDELT_ENABLED: bool = False

    # Sanction feed URLs
    OFAC_SDN_URL: str = "https://www.treasury.gov/ofac/downloads/sdn.xml"
    UN_SANCTIONS_URL: str = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

    # Admin seed
    ADMIN_EMAIL: str = "admin@vigil.com"
    ADMIN_PASSWORD: str = ""
    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()