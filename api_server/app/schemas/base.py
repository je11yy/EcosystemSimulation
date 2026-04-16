from typing import Optional

from pydantic import BaseModel


class Response(BaseModel):
    """Basic response model"""

    success: bool
    message: Optional[str] = None


class Position(BaseModel):
    """Position in 2D space"""

    x: float
    y: float


class Node(BaseModel):
    """Base node model with position"""

    id: int
    position: Position
