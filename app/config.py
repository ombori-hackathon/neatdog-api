from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/hackathon"
    debug: bool = True
    jwt_secret_key: str = "change-me-in-production-use-env-var"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
