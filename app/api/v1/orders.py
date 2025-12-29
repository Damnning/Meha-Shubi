from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.order_service import OrderService
from app.schemas.order import OrderRead
from app.api.deps import get_current_user_id

router = APIRouter()

@router.post("/", response_model=OrderRead)
async def checkout(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = OrderService(db)
    try:
        return await service.create_order(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))