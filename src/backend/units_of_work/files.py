from common.unit_of_work import BaseORMUnitOfWork
from repository.orm import FileRepository, FileMetadataRepository, TrainDataRepository


class FileUnitOfWork(BaseORMUnitOfWork):
    async def __aenter__(self):
        await super().__aenter__()
        self.files = FileRepository(self._session)
        self.file_metadatas = FileMetadataRepository(self._session)
        self.train_data = TrainDataRepository(self._session)
        return self
