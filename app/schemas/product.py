from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum


class ProductBase(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    category_id: int
    specs: Dict[str, Any] = {}


class ProductCreate(ProductBase):
    # Теперь мы явно ждем описание от фронтенда (оно может быть пустым)
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


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    specs: Optional[Dict[str, Any]] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None


class GenerateDescriptionRequest(BaseModel):
    name: str
    specs: Dict[str, Any]


class GenerateDescriptionResponse(BaseModel):
    description: str
