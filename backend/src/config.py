from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SUPABASE_URL: str = Field(..., alias="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., alias="PUSHABLE_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., alias="SECRET_KEY")
    GOOGLE_API_KEY: str = Field(..., alias="GOOGLE_API_KEY")
    SERP_API_KEY: str = Field(..., alias="SERP_API_KEY")
    FIRECRAWL_API_KEY: str = Field(..., alias="FIRECRAWL_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()  # pyright: ignore[reportCallIssue]
