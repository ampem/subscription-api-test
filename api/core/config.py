from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str = "postgresql+psycopg2://shade:shade@localhost:5432/shade"

    class Config:
        env_file = ".env"


settings = Settings()
