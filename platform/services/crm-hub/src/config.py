
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Общие настройки
    APP_NAME: str = "CRM Hub Service"
    APP_VERSION: str = "3.1"

    # Настройки базы данных
    DATABASE_URL: str = Field(default=..., env="DATABASE_URL")

    # Настройки Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Настройки Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS"
    )

    # Настройки секретов
    SECRET_KEY: str = Field(default=..., env="SECRET_KEY")

    # Настройки OAuth
    AMOCRM_CLIENT_ID: str = Field(default=..., env="AMOCRM_CLIENT_ID")
    AMOCRM_CLIENT_SECRET: str = Field(default=..., env="AMOCRM_CLIENT_SECRET")

    BITRIX24_CLIENT_ID: str = Field(default=..., env="BITRIX24_CLIENT_ID")
    BITRIX24_CLIENT_SECRET: str = Field(default=..., env="BITRIX24_CLIENT_SECRET")

    MEGAPLAN_CLIENT_ID: str = Field(default=..., env="MEGAPLAN_CLIENT_ID")
    MEGAPLAN_CLIENT_SECRET: str = Field(default=..., env="MEGAPLAN_CLIENT_SECRET")

    SALESFORCE_CLIENT_ID: str = Field(default=..., env="SALESFORCE_CLIENT_ID")
    SALESFORCE_CLIENT_SECRET: str = Field(default=..., env="SALESFORCE_CLIENT_SECRET")

    HUBSPOT_CLIENT_ID: str = Field(default=..., env="HUBSPOT_CLIENT_ID")
    HUBSPOT_CLIENT_SECRET: str = Field(default=..., env="HUBSPOT_CLIENT_SECRET")

    PIPEDRIVE_CLIENT_ID: str = Field(default=..., env="PIPEDRIVE_CLIENT_ID")
    PIPEDRIVE_CLIENT_SECRET: str = Field(default=..., env="PIPEDRIVE_CLIENT_SECRET")

    # Настройки логирования
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
