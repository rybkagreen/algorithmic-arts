from pydantic import BaseModel, Field
from pydantic-settings import BaseSettings


class DatabaseSettings(BaseModel):
    host: str = Field(default="postgres")
    port: int = Field(default=5432)
    user: str = Field(default="algo_user")
    password: str = Field(default="password")
    name: str = Field(default="algorithmic_arts")
    pool_size: int = Field(default=20)
    max_overflow: int = Field(default=40)


class RedisSettings(BaseModel):
    host: str = Field(default="redis")
    port: int = Field(default=6379)
    db: int = Field(default=0)
    cache_ttl: int = Field(default=3600)


class KafkaSettings(BaseModel):
    bootstrap_servers: str = Field(default="kafka:9092")
    producer_group_id: str = Field(default="company-service-producer")
    consumer_group_id: str = Field(default="company-service-consumer")
    auto_offset_reset: str = Field(default="earliest")


class ElasticsearchSettings(BaseModel):
    host: str = Field(default="elasticsearch")
    port: int = Field(default=9200)
    index_name: str = Field(default="companies")


class Settings(BaseSettings):
    env: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    elasticsearch: ElasticsearchSettings = Field(default_factory=ElasticsearchSettings)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


settings = Settings()