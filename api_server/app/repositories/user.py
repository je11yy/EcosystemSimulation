from sqlalchemy import select

from app.models import User
from app.repositories.base import Repository


class UserRepository(Repository):
    async def get_by_nickname(self, nickname: str) -> User | None:
        stmt = select(User).where(User.nickname == nickname)
        return await self.session.scalar(stmt)

    async def create(self, nickname: str, hashed_password: str) -> User:
        user = User(nickname=nickname, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return user
