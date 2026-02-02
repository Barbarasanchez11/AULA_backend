from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database URL completa (opcional, se puede construir)
    database_url: Optional[str] = None
    
    # Variables individuales de PostgreSQL (opcionales)
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[str] = None
    
    debug: bool = False
    app_name: str = "AULA+"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Si no hay database_url pero hay variables individuales, construirla
        if not self.database_url and self.postgres_user:
            # Si estamos en Docker, usar el nombre del servicio, sino localhost
            import os
            host = self.postgres_host or (os.getenv("POSTGRES_HOST", "localhost"))
            # Si no hay POSTGRES_HOST en env, intentar detectar si estamos en Docker
            if host == "localhost" and os.path.exists("/.dockerenv"):
                host = "postgres"  # Nombre del servicio en docker-compose
            port = self.postgres_port or "5432"
            self.database_url = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{host}:{port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar variables extra en lugar de fallar

settings = Settings()
