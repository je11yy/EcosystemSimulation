from typing import Optional

from pydantic import BaseModel


class Response(BaseModel):
    success: bool
    message: Optional[str] = None


class Position(BaseModel):
    x: float
    y: float


class Node(BaseModel):
    id: int
    position: Position
