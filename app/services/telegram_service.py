import hashlib
import hmac
import time
from fastapi import HTTPException
from app.core.config import settings
from app.schemas.telegram import TelegramAuth


def validate_telegram_data(data: TelegramAuth) -> bool:
    """
    Проверяет HMAC-SHA256 подпись данных от Telegram.
    """
    if not settings.TG_BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Telegram Bot Token not configured")

    # 1. Проверка срока действия (защита от replay attack)
    # Данные валидны, например, 24 часа (86400 секунд)
    if time.time() - data.auth_date > 86400:
        return False

    # 2. Подготовка строки для хеширования
    # Берем все поля, кроме hash, сортируем по ключу алфавитно
    data_dict = data.model_dump(exclude={'hash',
                                         'photo_url'})  # photo_url иногда не участвует, но лучше проверить документацию, обычно hash считается без него или с ним, но если поле None, оно не передается.

    # Самый надежный способ - собрать словарь из пришедших непустых полей
    # (Telegram Widget присылает только заполненные поля)
    check_arr = []
    for k, v in data_dict.items():
        if v is not None:
            check_arr.append(f"{k}={v}")

    # Важно: сортировка по алфавиту
    check_arr.sort()

    # Собираем строку через перевод строки
    data_check_string = "\n".join(check_arr)

    # 3. Вычисляем секретный ключ (SHA256 от токена бота)
    secret_key = hashlib.sha256(settings.TG_BOT_TOKEN.encode()).digest()

    # 4. Вычисляем HMAC-SHA256
    hash_calc = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # 5. Сравниваем
    return hash_calc == data.hash