import asyncio
from openai import AsyncOpenAI
from app.core.config import settings


class LLMService:
    """
    Базовый интерфейс.
    """

    async def generate_description(self, product_name: str, specs: dict) -> str:
        raise NotImplementedError


class MockLLMService(LLMService):
    """
    Заглушка. Работает, если нет токена.
    """

    async def generate_description(self, product_name: str, specs: dict) -> str:
        await asyncio.sleep(0.5)
        specs_str = ", ".join([f"{k}: {v}" for k, v in specs.items()])
        return (
            f"ОПИСАНИЕ ОТ AI (MOCK): Это заглушка, так как токен OpenRouter не найден. "
            f"Товар '{product_name}' с характеристиками: {specs_str}."
        )


class OpenRouterLLMService(LLMService):
    """
    Реальная интеграция с OpenRouter (доступ к GPT-4, Claude 3, Llama 3 и др).
    """

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        # Модель можно поменять на любую доступную в OpenRouter
        # "mistralai/mistral-7b-instruct:free" - полностью бесплатная
        # "openai/gpt-3.5-turbo" - дешевая
        # "meta-llama/llama-3-8b-instruct:free" - тоже бывает бесплатной
        self.model = settings.LLM_MODEL

    async def generate_description(self, product_name: str, specs: dict) -> str:
        # Формируем красивый промпт
        specs_str = "\n".join([f"- {k}: {v}" for k, v in specs.items()])

        system_prompt = (
            "Ты опытный копирайтер для интернет-магазина дорогих товаров (меха, шубы). "
            "Твоя задача — написать привлекательное, продающее описание товара на русском языке. "
            "Используй элегантный стиль, подчеркни качество."
        )

        user_prompt = (
            f"Напиши описание для товара:\n"
            f"Название: {product_name}\n"
            f"Характеристики:\n{specs_str}\n\n"
            f"Требования: Не более 3-4 предложений. Без вводных фраз ('Вот описание...'). Только текст."
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.7,
                # OpenRouter требует эти заголовки для корректной работы и статистики
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",  # URL твоего сайта
                    "X-Title": "Fur Shop API",  # Название твоего приложения
                },
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenRouter Error: {e}")
            # Возвращаем заглушку в случае ошибки, чтобы фронтенд не падал
            return f"Не удалось сгенерировать описание (Ошибка AI). Характеристики: {specs_str}"


def get_llm_service() -> LLMService:
    """
    Фабрика: если токен есть в .env - возвращаем OpenRouter, иначе Mock.
    """
    if settings.OPENROUTER_KEY and settings.OPENROUTER_KEY.strip():
        return OpenRouterLLMService()

    print("WARNING: OPENROUTER_KEY not found via settings. Using Mock Service.")
    return MockLLMService()