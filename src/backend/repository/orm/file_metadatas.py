from common.repository.orm import BaseORMRepository
from models.orm import FileMetadata


class FileMetadataRepository(BaseORMRepository):
    Model = FileMetadata
