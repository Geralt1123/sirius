from common.repository.orm import BaseORMRepository
from models.orm import File


class FileRepository(BaseORMRepository):
    Model = File
