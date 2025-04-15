from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config(BaseSettings):
    POSTGRES_USERNAME: str = "postgres"
    POSTGRES_PASSWORD: str = "root"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DATABASE: str = "mydatabase"

    @property
    def DB_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DATABASE}"

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    TOKEN_SECRET_KEY: str = "secret_key"
    ACCESS_TOKEN_EXPIRE_IN: int = 6000  # 10 minutes
    REFRESH_TOKEN_EXPIRE_IN: int = 60 * 60 * 24 * 7  # 7 days


config = Config()
