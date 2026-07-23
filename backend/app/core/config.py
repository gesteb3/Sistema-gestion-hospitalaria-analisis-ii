from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Settings(BaseSettings):
    app_name: str = "Sistema de Gestión Hospitalaria"
    app_version: str = "0.2.0"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:4200"

    oracle_user: str = "hms_app"
    oracle_password: str = "HmsApp12345"
    oracle_host: str = "localhost"
    oracle_port: int = 1521
    oracle_service: str = "FREEPDB1"

    jwt_secret_key: str = (
        "cambiar-esta-clave-secreta-en-produccion-2026"
    )
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    admin_username: str = "admin"
    admin_password: str = "Admin12345"
    admin_email: str = "admin@hospital.com"
    admin_nombres: str = "Administrador"
    admin_apellidos: str = "General"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="oracle+oracledb",
            username=self.oracle_user,
            password=self.oracle_password,
            host=self.oracle_host,
            port=self.oracle_port,
            query={
                "service_name": self.oracle_service,
            },
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()