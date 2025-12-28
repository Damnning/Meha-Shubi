from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class ProductBase(BaseModel):
    name: str
    price: float = Field(..., gt=0)  # Цена должна быть больше 0
    category_id: int
    specs: Dict[str, Any] = {}  # JSON характеристики


class ProductCreate(ProductBase):
    # Описание и картинка могут отсутствовать при создании,
    # так как описание генерит ИИ, а картинку грузим отдельным полем/шагом
    description: Optional[str] = None


class ProductRead(ProductBase):
    id: int
    image_url: Optional[str] = None
    description: Optional[str] = None

    # Чтобы подтянуть имя категории в ответе (если нужно)
    # category: Optional[CategoryRead] = None

    model_config = ConfigDict(from_attributes=True)


class SortOption(str, Enum):
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"
    NEWEST = "newest"


class ProductFilter(BaseModel):
    category_id: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    # Фильтр по JSON характеристикам (например, {"color": "black"})
    # В реальном проекте это часто реализуют сложнее, но для базы хватит
    specs_filter: Optional[Dict[str, Any]] = None

    sort_by: SortOption = SortOption.NEWEST
    page: int = 1
    limit: int = 10