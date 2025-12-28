from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Базовая схема (общие поля)
class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

# Схема для создания (входные данные)
class CategoryCreate(CategoryBase):
    pass

# Схема для чтения (выходные данные)
class CategoryRead(CategoryBase):
    id: int
    # Forward reference для вложенных категорий
    children: List["CategoryRead"] = []

    model_config = ConfigDict(from_attributes=True)