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
    
    # CORS Configuration
    allow_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Groq API configuration (Legacy)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.1-8b-instant"  
    
    # Hugging Face configuration
    hf_api_key: Optional[str] = None
    hf_model_id: str = "BSC-LT/salamandra-7b-instruct"
    llm_temperature: float = 0.7  
    llm_max_tokens: int = 2048  

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        import os
        
        # 1. Prioridad absoluta a DATABASE_URL (inyectada por Railway)
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            # Railway inyecta postgres://, pero necesitamos postgresql+asyncpg://
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            self.database_url = db_url
        
        # 2. Si no hay DATABASE_URL, intentar construirla desde variables individuales de Railway (PGHOST, etc.)
        elif not self.database_url:
            user = os.getenv("PGUSER") or self.postgres_user
            password = os.getenv("PGPASSWORD") or self.postgres_password
            host = os.getenv("PGHOST") or self.postgres_host
            port = os.getenv("PGPORT") or self.postgres_port or "5432"
            db_name = os.getenv("PGDATABASE") or self.postgres_db
            
            if user and password and host and db_name:
                self.database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
            else:
                # Si estamos local y no hay nada, usar el fallback de desarrollo
                if not os.getenv("RAILWAY_ENVIRONMENT"):
                    host = host or "localhost"
                    user = user or "user"
                    password = password or "pass"
                    db_name = db_name or "db"
                    self.database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignorar variables extra en lugar de fallar

settings = Settings()
