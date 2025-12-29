from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload  # <--- Нужно добавить

from app.models.models import Order, OrderItem
from app.services.cart_service import CartService


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cart_service = CartService(db)

    async def create_order(self, user_id: int) -> Order:
        # 1. Получаем корзину
        cart = await self.cart_service.get_or_create_cart(user_id)

        if not cart.items:
            raise ValueError("Cart is empty")

        # 2. Считаем сумму и создаем объекты OrderItem
        total_price = 0.0
        order_items = []

        for item in cart.items:
            price = item.product.price
            total_price += price * item.quantity

            order_items.append(OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=price  # Фиксируем цену!
            ))

        # 3. Создаем заказ
        order = Order(
            user_id=user_id,
            total_price=total_price,
            items=order_items
        )
        self.db.add(order)

        # 4. Очищаем корзину (удаляем CartItems)
        for item in cart.items:
            await self.db.delete(item)

        # 5. Коммит
        await self.db.commit()

        # 6. ВАЖНО: Вместо refresh делаем явный запрос с подгрузкой items.
        # Это предотвращает ошибку MissingGreenlet при сериализации ответа.
        query = (
            select(Order)
            .where(Order.id == order.id)
            .options(selectinload(Order.items))
        )

        result = await self.db.execute(query)
        return result.scalar_one()