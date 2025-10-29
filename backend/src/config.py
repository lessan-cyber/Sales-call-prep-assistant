from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str = Field(..., alias="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., alias="PUSHABLE_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., alias="SECRET_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # pyright: ignore[reportCallIssue]
