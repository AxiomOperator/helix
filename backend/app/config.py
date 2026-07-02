from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Linux Command Center", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://command_center:command_center@postgres:5432/command_center",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    frontend_origin: str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_email: str = Field(default="admin@example.com", alias="ADMIN_EMAIL")
    admin_password: str = Field(default="change-me-now", alias="ADMIN_PASSWORD")
    admin_display_name: str = Field(default="Administrator", alias="ADMIN_DISPLAY_NAME")
    session_cookie_name: str = Field(default="lcc_session", alias="SESSION_COOKIE_NAME")
    session_expire_hours: int = Field(default=8, alias="SESSION_EXPIRE_HOURS")
    session_cookie_secure: bool = Field(default=False, alias="SESSION_COOKIE_SECURE")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
