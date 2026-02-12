from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .repositories.user_repository import UserRepository
from .services.jwt_service import JWTService

# Создаем асинхронный engine
engine = create_async_engine(
    f"postgresql+asyncpg://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.name}",
    echo=False,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
)

# Создаем sessionmaker
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def get_db():
    return async_session_maker()


def get_redis():
    return Redis(
        host=settings.redis.host, port=settings.redis.port, db=settings.redis.db
    )


def get_jwt_service():
    redis = get_redis()
    return JWTService(redis)


def get_user_repository():
    db = get_db()
    return UserRepository(db)
