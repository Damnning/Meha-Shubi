import uuid
from starlette.requests import Request
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.oauth import oauth
from app.core.security import create_access_token
from app.schemas.user import UserCreate, Token
from app.services.user_service import UserService


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)

    async def get_login_redirect(self, provider: str, request: Request, redirect_uri: str):
        """
        Генерирует редирект на сайт провайдера.
        """
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail=f"Provider {provider} not supported")

        from app.core.config import settings
        real_redirect_uri = f"{settings.BASE_URL}/api/v1/auth/callback/{provider}"

        print(f"DEBUG: Sending Redirect URI to VK: {real_redirect_uri}")

        kwargs = {}
        if provider == 'vk':
            kwargs['scope'] = 'email'
        elif provider == 'yandex':
            kwargs['scope'] = 'login:email'


        return await client.authorize_redirect(request, redirect_uri)

    async def authenticate_social_user(self, provider: str, request: Request) -> dict:
        """
        Обрабатывает callback, получает email, создает юзера (если надо) и выдает токен.
        """
        client = oauth.create_client(provider)
        if not client:
            raise HTTPException(status_code=400, detail="Unknown provider")

        from app.core.config import settings
        client = oauth.create_client(provider)

        request.scope["starlette.app"].state.redirect_uri = f"{settings.BASE_URL}/api/v1/auth/callback/{provider}"

        try:
            # Обмениваем код на токен
            token = await client.authorize_access_token(request)
        except Exception as e:
            print(f"OAuth Error: {e}")
            raise HTTPException(status_code=400, detail="OAuth connection error")

        user_email = None

        # --- Специфика VK ---
        if provider == 'vk':
            # VK часто отдает email прямо в ответе с токеном
            user_email = token.get('email')

        # --- Специфика Yandex ---
        elif provider == 'yandex':
            # Yandex требует отдельного запроса за инфо
            try:
                resp = await client.get('info', token=token)
                user_info = resp.json()
                user_email = user_info.get('default_email')
            except Exception:
                raise HTTPException(status_code=400, detail="Failed to fetch user info from Yandex")

        # Если email не удалось достать (например, юзер запретил доступ к email в VK)
        if not user_email:
            raise HTTPException(status_code=400, detail=f"Could not retrieve email from {provider}")

        # --- Логика Users (Find or Create) ---
        user = await self.user_service.get_by_email(user_email)

        if not user:
            # Создаем нового пользователя с рандомным паролем
            random_password = str(uuid.uuid4())
            user_in = UserCreate(email=user_email, password=random_password)
            user = await self.user_service.create_user(user_in)

        # --- Выдача токена ---
        return {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
        }