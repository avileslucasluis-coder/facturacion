from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Facturación Electrónica Empresarial"
    jwt_secret_key: str = "change_this_secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    database_url: str = "sqlite:///data/billing_system.db"
    openai_api_key: Optional[str] = None
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    static_dir: str = "static"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
