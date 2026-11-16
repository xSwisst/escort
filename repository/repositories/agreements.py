from sqlalchemy.ext.asyncio import AsyncSession

from repository.models.settings import Agreement
from repositories.base import BaseRepository


class AgreementRepository(BaseRepository[Agreement]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Agreement)
