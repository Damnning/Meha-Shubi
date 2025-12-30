from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, Token
from app.core.security import create_access_token

import uuid
from app.schemas.telegram import TelegramAuth
from app.services.telegram_service import validate_telegram_data
from app.services.user_service import UserService
router = APIRouter()


@router.post("/register", response_model=UserRead)
async def register(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    # 1. Проверяем бизнес-логику (существование)
    if await service.get_by_email(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists.",
        )

    # 2. Делегируем создание сервису
    return await service.create_user(user_in)


@router.post("/login", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@router.post("/login/telegram", response_model=Token)
async def telegram_login(
        tg_data: TelegramAuth,
        db: AsyncSession = Depends(get_db)
):
    # 1. Валидация подписи
    if not validate_telegram_data(tg_data):
        raise HTTPException(status_code=400, detail="Invalid Telegram data or signature")

    # 2. Логика пользователя
    # Telegram НЕ отдает Email. У нас есть два пути:
    # А) Создать фейковый email (простой путь)
    # Б) Добавить поле telegram_id в таблицу User (правильный путь)

    # Идем по пути А (чтобы не менять БД прямо сейчас):
    fake_email = f"{tg_data.id}@telegram.user"

    service = UserService(db)
    user = await service.get_by_email(fake_email)

    if not user:
        # Регистрируем нового
        # Пароль рандомный, так как вход только через ТГ
        user_in = UserCreate(email=fake_email, password=str(uuid.uuid4()))
        user = await service.create_user(user_in)

    # 3. Выдаем токен
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }