from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductRead, ProductFilter, ProductUpdate, GenerateDescriptionRequest, \
    GenerateDescriptionResponse
from app.services.llm_service import get_llm_service
from app.services.product_service import ProductService
from app.services.s3_service import S3Service

router = APIRouter()

# 1. Загрузка изображения
@router.post("/upload-image")
async def upload_product_image(
    file: UploadFile = File(...)
):
    """
    Загружает файл в S3 и возвращает публичный URL.
    """
    s3_service = S3Service()
    url = await s3_service.upload_file(file)
    return {"url": url}

# 1. Отдельная ручка для AI
@router.post("/generate-description", response_model=GenerateDescriptionResponse)
async def generate_description(
    req: GenerateDescriptionRequest
):
    """
    Генерирует описание товара с помощью LLM (или Mock), не сохраняя товар в БД.
    """
    llm_service = get_llm_service()
    description = await llm_service.generate_description(req.name, req.specs)
    return {"description": description}


# 2. Обновленный эндпоинт создания (просто сохраняет)
@router.post("/", response_model=ProductRead)
async def create_product(
    product_in: ProductCreate,
    image_url: str = None,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    # Теперь product_in уже содержит description, который прислал фронтенд
    return await service.create_product(product_in, image_url)

# 3. Поиск и фильтрация (ТЗ: POST метод для фильтрации)
@router.post("/search", response_model=List[ProductRead])
async def search_products(
    filters: ProductFilter,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.get_filtered_products(filters)

# 4. Детальная страница
@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    product = await service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_in: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    product = await service.update_product(product_id, product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    deleted = await service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}