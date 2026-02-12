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
    session_ttl: int = Field(default=86400)


class JWTSettings(BaseModel):
    algorithm: str = Field(default="RS256")
    access_token_expire_minutes: int = Field(default=15)
    refresh_token_expire_days: int = Field(default=30)
    private_key: str = Field(default="")
    public_key: str = Field(default="")


class KafkaSettings(BaseModel):
    bootstrap_servers: str = Field(default="kafka:9092")
    consumer_group_id: str = Field(default="algo-platform")
    auto_offset_reset: str = Field(default="earliest")
    max_poll_records: int = Field(default=500)


class OAuthSettings(BaseModel):
    yandex: dict = Field(default_factory=lambda: {
        "client_id": "",
        "client_secret": ""
    })
    google: dict = Field(default_factory=lambda: {
        "client_id": "",
        "client_secret": ""
    })
    vk: dict = Field(default_factory=lambda: {
        "client_id": "",
        "client_secret": ""
    })


class EmailSettings(BaseModel):
    host: str = Field(default="smtp.yandex.ru")
    port: int = Field(default=587)
    user: str = Field(default="noreply@algorithmic-arts.ru")
    password: str = Field(default="")
    from_name: str = Field(default="ALGORITHMIC ARTS")


class Settings(BaseSettings):
    env: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    oauth: OAuthSettings = Field(default_factory=OAuthSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


settings = Settings()