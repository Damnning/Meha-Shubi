from pydantic import BaseModel, ConfigDict, Field
from app.schemas.product import ProductRead


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemRead(BaseModel):
    id: int
    quantity: int
    product: ProductRead  # Вкладываем полные данные о продукте

    model_config = ConfigDict(from_attributes=True)


class CartRead(BaseModel):
    id: int
    items: list[CartItemRead] = []

    # Вычисляемое поле для удобства фронтенда
    @property
    def total_price(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

    model_config = ConfigDict(from_attributes=True)


class CartItemUpdate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0) # Количество должно быть больше 0