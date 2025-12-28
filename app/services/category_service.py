from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

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
        return category

    async def get_all_categories(self) -> list[Category]:
        """
        Возвращает дерево категорий.
        Мы берем только корневые категории (где parent_id IS NULL),
        а SQLAlchemy через selectinload рекурсивно подтянет children.
        """
        query = (
            select(Category)
            .filter(Category.parent_id == None)  # Только корни
            .options(selectinload(Category.children))  # Жадная загрузка детей
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_category_by_id(self, category_id: int) -> Category | None:
        return await self.db.get(Category, category_id)