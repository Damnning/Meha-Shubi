from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm.attributes import set_committed_value  # <--- ВАЖНЫЙ ИМПОРТ

from app.models.models import Category
from app.schemas.category import CategoryCreate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, schema: CategoryCreate) -> Category:
        category = Category(**schema.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        # ВМЕСТО category.children = []
        # Мы жестко устанавливаем значение, минуя попытку загрузки из БД
        set_committed_value(category, "children", [])

        return category

    async def get_all_categories(self) -> list[Category]:
        """
        Загрузка дерева за 1 запрос + ручная сборка.
        """
        # 1. Загружаем все категории
        result = await self.db.execute(select(Category))
        categories = result.scalars().all()

        category_map = {c.id: c for c in categories}

        # 2. Инициализируем пустые списки для всех (через set_committed_value)
        for cat in categories:
            set_committed_value(cat, "children", [])

        # 3. Раскладываем по папкам
        roots = []
        for cat in categories:
            if cat.parent_id is None:
                roots.append(cat)
            else:
                parent = category_map.get(cat.parent_id)
                if parent:
                    parent.children.append(cat)

        return roots

    async def get_category_by_id(self, category_id: int) -> Category | None:
        category = await self.db.get(Category, category_id)
        if category:
            set_committed_value(category, "children", [])
        return category