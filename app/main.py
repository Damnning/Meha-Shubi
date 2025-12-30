import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.session import engine, Base
from app.api.v1 import categories, products, cart, orders, auth
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

from fastapi.responses import HTMLResponse
from app.core.config import settings

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

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET)

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


@app.get("/login_test", response_class=HTMLResponse)
async def telegram_test_page():
    bot_name = "meha_shubi_auth_bot"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Login Test</title>
        <style>
            body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; padding-top: 50px; }}
            #response {{ margin-top: 20px; padding: 10px; border: 1px solid #ccc; background: #f9f9f9; white-space: pre-wrap; display: none; }}
        </style>
    </head>
    <body>
        <h1>Вход через Telegram</h1>
        <p>Эта страница отдается с домена: <b>{settings.BASE_URL}</b></p>

        <!-- Виджет Телеграм -->
        <script async src="https://telegram.org/js/telegram-widget.js?22" 
                data-telegram-login="{bot_name}" 
                data-size="large" 
                data-onauth="onTelegramAuth(user)" 
                data-request-access="write"></script>

        <div id="response"></div>

        <script type="text/javascript">
          function onTelegramAuth(user) {{
            const resultDiv = document.getElementById('response');
            resultDiv.style.display = 'block';
            resultDiv.innerText = "Processing...";

            // Отправляем данные на наш же бэкенд
            fetch('/api/v1/auth/login/telegram', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify(user)
            }})
            .then(response => response.json())
            .then(data => {{
                console.log(data);
                if (data.access_token) {{
                    resultDiv.innerHTML = "✅ <b>Успех!</b><br>Токен получен:<br><br>" + data.access_token;
                }} else {{
                    resultDiv.innerText = "❌ Ошибка: " + JSON.stringify(data, null, 2);
                }}
            }})
            .catch(error => {{
                resultDiv.innerText = "Network Error: " + error;
            }});
          }}
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)