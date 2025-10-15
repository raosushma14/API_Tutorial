from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")
    app_name: str = Field("Employee Workforce API", alias="APP_NAME")
    app_debug: bool = Field(False, alias="APP_DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
