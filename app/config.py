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
    
    # Groq API configuration
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"  
    groq_temperature: float = 0.7  
    groq_max_tokens: int = 1000  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Si no hay database_url pero hay variables individuales, construirla
        if not self.database_url and self.postgres_user:
            # Si estamos en Docker, usar el nombre del servicio, sino localhost
            import os
            is_docker = os.path.exists("/.dockerenv") or os.getenv("IS_DOCKER") == "true"
            
            host = self.postgres_host
            if is_docker:
                host = "postgres"
            elif not host:
                host = "localhost"
                
            port = self.postgres_port or "5432"
            self.database_url = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{host}:{port}/{self.postgres_db}"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar variables extra en lugar de fallar

settings = Settings()
