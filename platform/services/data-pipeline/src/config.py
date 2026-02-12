from pydantic import BaseSettings


class Settings(BaseSettings):
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    
    # Redis
    REDIS_URL: str = "redis://redis:6379/1"
    
    # PostgreSQL
    POSTGRES_DSN: str = "postgresql+asyncpg://data_pipeline:password@postgres:5432/data_pipeline"
    
    # Elasticsearch
    ES_HOST: str = "elasticsearch:9200"
    
    # API Keys
    CRUNCHBASE_API_KEY: str = ""
    KONTUR_FOKUS_API_KEY: str = ""
    
    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()