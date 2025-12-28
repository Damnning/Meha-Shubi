from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, asc
from app.models.models import Product
from app.schemas.product import ProductCreate, ProductFilter
from app.services.llm_service import get_llm_service


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service = get_llm_service()

    async def create_product(self, schema: ProductCreate, image_url: str = None) -> Product:
        """
        1. Генерируем описание через AI.
        2. Создаем запись в БД.
        """
        # Генерация описания (фоновая задача или await)
        # Здесь используем await, но в реале лучше Celery/BackgroundTasks для долгих запросов
        ai_description = await self.llm_service.generate_description(
            schema.name,
            schema.specs
        )

        product_data = schema.model_dump()
        product_data["description"] = ai_description
        product_data["image_url"] = image_url

        product = Product(**product_data)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
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