from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from app.models.models import Product
from app.schemas.product import ProductCreate, ProductFilter, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, schema: ProductCreate, image_url: str = None) -> Product:
        product_data = schema.model_dump()
        product_data["image_url"] = image_url

        # product_data["description"] берется напрямую из schema (от пользователя)

        product = Product(**product_data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        # На всякий случай для Pydantic v2 и lazy loading
        # Если вдруг schema вернет description, его и так вернет объект.
        # Но если нужно что-то сложное, можно перезапросить, как мы делали в Orders.
        # Для простого объекта refresh обычно достаточно.
        return product

    async def get_product_by_id(self, product_id: int) -> Product | None:
        return await self.db.get(Product, product_id)

    async def get_filtered_products(self, filters: ProductFilter) -> list[Product]:
        """
        Сложная фильтрация товаров.
        """
        query = select(Product)

        # 1. Фильтр по категории
        if filters.category_id:
            query = query.filter(Product.category_id == filters.category_id)

        # 2. Фильтр по цене
        if filters.price_min is not None:
            query = query.filter(Product.price >= filters.price_min)
        if filters.price_max is not None:
            query = query.filter(Product.price <= filters.price_max)

        # 3. Фильтр по JSON specs (PostgreSQL specific)
        # Если передан словарь {"color": "white"}, ищем точное совпадение внутри JSONB
        if filters.specs_filter:
            for key, value in filters.specs_filter.items():
                # Синтаксис SQLA для JSON: Product.specs[key].astext == value
                # Нужно приведение типов, если value не строка, но для простоты берем строки
                query = query.filter(Product.specs[key].astext == str(value))

        # 4. Сортировка
        if filters.sort_by == "price_asc":
            query = query.order_by(asc(Product.price))
        elif filters.sort_by == "price_desc":
            query = query.order_by(desc(Product.price))
        else:
            query = query.order_by(desc(Product.id))  # Newest

        # 5. Пагинация
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_product(self, product_id: int, schema: ProductUpdate) -> Product | None:
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        # Обновляем только те поля, которые пришли
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> bool:
        product = await self.get_product_by_id(product_id)
        if not product:
            return False

        await self.db.delete(product)
        await self.db.commit()
        return True
