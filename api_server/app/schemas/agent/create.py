from typing import Optional

from pydantic import BaseModel

from app.enums import AgentSex


class AgentCreate(BaseModel):
    territory_id: int
    genome_id: Optional[int] = None
    sex: AgentSex
