import io
from uuid import uuid4, UUID
from dataclasses import dataclass

import cv2
import numpy as np

from common.exceptions import ControllerException
from common.models.s3 import S3Model
from common.repository import S3Repository
from interfaces import AsyncService
from models.orm import File
from units_of_work import FileUnitOfWork


@dataclass(kw_only=True, slots=True, frozen=True)
class UploadFileController(AsyncService):
    """Загрузка файла и добавление записи о нём в БД"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
        file: bytes
    ):
        async with self.orm_unit_of_work as orm_uow:
            M, N = 128, 1024

            arr = file.root
            arr = np.array(arr)
            if isinstance(arr, np.ndarray):
                if arr.dtype == np.float32 or arr.dtype == np.float64:
                    arr = (arr * 255).astype(np.uint8)
            else:
                raise ValueError("Данные в файле не являются numpy массивом.")

            tiles = [arr[x:x + M, y:y + N] for x in range(0, arr.shape[0], M) for y in range(0, arr.shape[1], N)]
            previous_file = None
            files = []
            for tile in tiles:
                file_id = uuid4()
                s3_model = S3Model(
                    bucket_name="sirius",
                    object_name=str(file_id),
                    data=io.BytesIO(tile.tobytes()),
                    length=tile.size,
                )
                self.storage_repository.insert(s3_model, None)
                await orm_uow.files.insert(
                    File(
                        id=file_id,
                        previous_file=previous_file if previous_file else None
                    )
                )
                files.append(file_id)
                previous_file = file_id
            await orm_uow.commit()
            cv2.GaussianBlur
        return files


@dataclass(kw_only=True, slots=True, frozen=True)
class DownloadFileController(AsyncService):
    """Получение файла"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
        file_id: UUID
    ):
        file_bytes = self.storage_repository.get(
            bucket_name="sirius", object_name=str(file_id)
        )
        image = np.reshape(np.frombuffer(file_bytes, dtype=np.uint8), (128, 1024))

        return image


@dataclass(kw_only=True, slots=True, frozen=True)
class GetFileListController(AsyncService):
    """Получение списка изображений на разметку"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
    ):
        async with self.orm_unit_of_work as orm_uow:
            files = await orm_uow.files.get(is_final_image=True)

        return files
