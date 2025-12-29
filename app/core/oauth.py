from authlib.integrations.starlette_client import OAuth
from app.core.config import settings

oauth = OAuth()

# 1. Настройка VK
if settings.VK_CLIENT_ID:
    oauth.register(
        name='vk',
        client_id=settings.VK_CLIENT_ID,
        client_secret=settings.VK_CLIENT_SECRET,
        authorize_url='https://oauth.vk.com/authorize',
        access_token_url='https://oauth.vk.com/access_token',
        api_base_url='https://api.vk.com/method/',
        # client_kwargs={'scope': 'email'}, # Запрашиваем email
    )

# 2. Настройка Yandex
if settings.YANDEX_CLIENT_ID:
    oauth.register(
        name='yandex',
        client_id=settings.YANDEX_CLIENT_ID,
        client_secret=settings.YANDEX_CLIENT_SECRET,
        authorize_url='https://oauth.yandex.ru/authorize',
        access_token_url='https://oauth.yandex.ru/token',
        api_base_url='https://login.yandex.ru/',
        client_kwargs={'scope': 'login:email'},
    )