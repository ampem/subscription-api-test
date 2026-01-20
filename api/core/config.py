from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str = "mysql+pymysql://shade:shade@localhost:3306/shade"

    class Config:
        env_file = ".env"


settings = Settings()
