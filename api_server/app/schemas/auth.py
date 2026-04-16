from pydantic import BaseModel, Field


class AuthCredentials(BaseModel):
    nickname: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)


class UserRead(BaseModel):
    id: int
    nickname: str
