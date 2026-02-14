from pydantic import BaseSettings


class Settings(BaseSettings):
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    
    # PostgreSQL
    POSTGRES_DSN: str = "postgresql+asyncpg://ai_core:password@postgres:5432/ai_core"
    
    # LLM Providers
    YANDEX_API_KEY: str = ""
    YANDEX_FOLDER_ID: str = ""
    GIGACHAT_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()