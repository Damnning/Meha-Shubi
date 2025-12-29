import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine, Base
from app.api.v1 import categories, products, cart, orders, auth

# Функция lifespan заменяет старые события @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем таблицы в БД при запуске (если их нет)
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Раскомментировать для сброса БД
        await conn.run_sync(Base.metadata.create_all)
    print("Database ready.")
    yield
    print("Shutting down.")

app = FastAPI(
    title="Fur Shop API",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем роутеры
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/v1/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Простой эндпоинт для проверки здоровья
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)