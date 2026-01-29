import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Aula Plus Backend"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
