from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.models import Cart, CartItem, Product


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, user_id: int) -> Cart:
        # Ищем корзину пользователя
        query = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(
                selectinload(Cart.items).selectinload(CartItem.product)
            )
        )
        result = await self.db.execute(query)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            # Рефреш нужен, чтобы подтянуть ID и пустой список items
            await self.db.refresh(cart, attribute_names=["items"])

        return cart

    async def add_item(self, user_id: int, product_id: int, quantity: int):
        cart = await self.get_or_create_cart(user_id)

        # Проверяем, есть ли уже этот товар в корзине
        existing_item = next((item for item in cart.items if item.product_id == product_id), None)

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            self.db.add(new_item)

        await self.db.commit()

        # ВАЖНОЕ ИЗМЕНЕНИЕ:
        # Вместо refresh(cart), который не подгружает вложенный product у нового item,
        # мы просто заново запрашиваем полную корзину со всеми связями.
        # Это гарантирует, что у всех items будет загружен product.
        return await self.get_or_create_cart(user_id)

    async def clear_cart(self, user_id: int):
        cart = await self.get_or_create_cart(user_id)
        # Удаляем все элементы корзины
        for item in cart.items:
            await self.db.delete(item)
        await self.db.commit()

    async def update_item_quantity(self, user_id: int, product_id: int, quantity: int):
        cart = await self.get_or_create_cart(user_id)

        # Ищем товар в корзине (в памяти, т.к. cart.items уже загружены)
        item_to_update = next((item for item in cart.items if item.product_id == product_id), None)

        if item_to_update:
            item_to_update.quantity = quantity
            self.db.add(item_to_update)
            await self.db.commit()

        # Возвращаем полную корзину, чтобы обновились итоги
        return await self.get_or_create_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int):
        cart = await self.get_or_create_cart(user_id)

        item_to_remove = next((item for item in cart.items if item.product_id == product_id), None)

        if item_to_remove:
            await self.db.delete(item_to_remove)
            await self.db.commit()

        return await self.get_or_create_cart(user_id)