from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Создаем движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Логирование SQL запросов (убрать в проде)
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Dependency для FastAPI (получение сессии в роуте)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session