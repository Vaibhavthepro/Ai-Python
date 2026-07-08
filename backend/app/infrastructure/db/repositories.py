from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.infrastructure.db.models import UserModel
from app.domain.entities.models import User
import uuid

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_data: dict) -> UserModel:
        db_user = UserModel(**user_data)
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return db_user
