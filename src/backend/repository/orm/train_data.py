from common.repository.orm import BaseORMRepository
from models.orm import TrainData


class TrainDataRepository(BaseORMRepository):
    Model = TrainData
