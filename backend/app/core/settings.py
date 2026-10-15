"""Application settings — everything via environment variables (see .env.example)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "ecommerce"
    postgres_password: str = "ecommerce"
    postgres_db: str = "ecommerce"

    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_db: str = "ecommerce"

    es_host: str = "localhost"
    es_port: int = 9200
    es_index: str = "orders"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_origin: str = "http://localhost:5173"

    sync_strategy: str = "dual_write"  # dual_write | polling
    poll_interval_seconds: int = 15

    @property
    def postgres_dsn(self) -> str:
        return (f"postgresql://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}")

    @property
    def mongo_dsn(self) -> str:
        return f"mongodb://{self.mongo_host}:{self.mongo_port}"

    @property
    def es_url(self) -> str:
        return f"http://{self.es_host}:{self.es_port}"


settings = Settings()
