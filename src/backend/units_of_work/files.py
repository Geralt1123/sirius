from common.unit_of_work import BaseORMUnitOfWork
from repository.orm import FileRepository


class FileUnitOfWork(BaseORMUnitOfWork):
    async def __aenter__(self):
        await super().__aenter__()
        self.files = FileRepository(self._session)
        return self
