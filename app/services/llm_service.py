import asyncio
from openai import AsyncOpenAI
from app.core.config import settings


class LLMService:
    """
    Базовый интерфейс для генерации текста.
    """

    async def generate_description(self, product_name: str, specs: dict) -> str:
        raise NotImplementedError


class MockLLMService(LLMService):
    """
    Заглушка для тестов
    """

    async def generate_description(self, product_name: str, specs: dict) -> str:
        # Имитация задержки сети
        await asyncio.sleep(0.5)
        specs_str = ", ".join([f"{k}: {v}" for k, v in specs.items()])
        return (
            f"ОПИСАНИЕ ОТ AI (MOCK): Роскошный товар '{product_name}'. "
            f"Обладает уникальными характеристиками: {specs_str}. "
            "Идеальный выбор для ценителей качества!"
        )


class OpenAILLMService(LLMService):
    """
    Реальная интеграция с OpenAI.
    """

    def __init__(self):
        # API key берется из os.environ["OPENAI_API_KEY"] автоматически библиотекой,
        # либо можно передать явно: api_key=settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key="your-api-key-here-or-from-env")

    async def generate_description(self, product_name: str, specs: dict) -> str:
        specs_str = ", ".join([f"{k}: {v}" for k, v in specs.items()])
        prompt = (
            f"Напиши продающее, привлекательное описание для товара интернет-магазина мехов.\n"
            f"Название: {product_name}\n"
            f"Характеристики: {specs_str}\n"
            f"Описание должно быть длиной 2-3 предложения."
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Или gpt-4
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Описание временно недоступно."


# Фабрика: возвращает нужный сервис в зависимости от настроек
def get_llm_service() -> LLMService:
    # Можно вынести флаг USE_MOCK_LLM в конфиг
    use_mock = True
    if use_mock:
        return MockLLMService()
    return OpenAILLMService()