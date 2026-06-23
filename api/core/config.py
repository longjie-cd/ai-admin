from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Admin"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
