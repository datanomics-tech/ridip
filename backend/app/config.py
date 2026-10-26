from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives in the repository root, two levels above this file.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str = "postgresql+psycopg://ridip:change-me@localhost:5432/ridip"


settings = Settings()