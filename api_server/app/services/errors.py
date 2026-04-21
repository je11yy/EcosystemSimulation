from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


async def get_or_404(session: AsyncSession, model: type, item_id: int, name: str) -> Any:
    item = await session.get(model, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return item
