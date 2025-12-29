from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.cart_service import CartService
from app.schemas.cart import CartRead, CartItemBase, CartItemUpdate
from app.api.deps import get_current_user_id

router = APIRouter()


@router.get("/", response_model=CartRead)
async def get_my_cart(
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    service = CartService(db)
    return await service.get_or_create_cart(user_id)


@router.post("/add", response_model=CartRead)
async def add_item_to_cart(
        item_in: CartItemBase,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    service = CartService(db)
    return await service.add_item(user_id, item_in.product_id, item_in.quantity)


@router.patch("/items", response_model=CartRead)
async def update_cart_item_quantity(
        item_in: CartItemUpdate,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    """
    Изменяет количество конкретного товара в корзине.
    """
    service = CartService(db)
    return await service.update_item_quantity(user_id, item_in.product_id, item_in.quantity)


@router.delete("/items/{product_id}", response_model=CartRead)
async def remove_item_from_cart(
        product_id: int,
        user_id: int = Depends(get_current_user_id),
        db: AsyncSession = Depends(get_db)
):
    """
    Полностью удаляет товар из корзины.
    """
    service = CartService(db)
    return await service.remove_item(user_id, product_id)
