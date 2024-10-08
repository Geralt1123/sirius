import io
import os
from uuid import uuid4, UUID
from dataclasses import dataclass

import numpy as np
import requests
from PIL import Image

from common.exceptions import ControllerException
from common.models.s3 import S3Model
from common.repository import S3Repository
from interfaces import AsyncService
from models.orm import File, FileMetadata, TrainData
from units_of_work import FileUnitOfWork
import cv2


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
            for i in range(0,4):
                tile = tiles[i]
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
            file_list = []
            for file in await orm_uow.files.list(is_final_image=True):
                file_list.append(file.id)

            return file_list


@dataclass(kw_only=True, slots=True, frozen=True)
class AddFilterController(AsyncService):
    """Применение фильтра"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
        files_id: list,
        method: str,
        meta: dict
    ):
        async with self.orm_unit_of_work as orm_uow:
            update_files_id = []
            for file_id in files_id:
                #  Получаем файл из хранилища
                file_bytes = self.storage_repository.get(
                    bucket_name="sirius", object_name=str(file_id)
                )
                #  Преобразуем в массив
                image = np.reshape(np.frombuffer(file_bytes, dtype=np.uint8), (128, 1024))

                match method:
                    case "gaus":

                        gaus_core_x = int(meta.get("gaus_core_x"))
                        gaus_core_y = int(meta.get("gaus_core_y"))
                        gaus_sigma_x = int(meta.get("gaus_sigma_x"))
                        gaus_sigma_y = int(meta.get("gaus_sigma_y"))

                        #  Применяем метод
                        update_image = cv2.GaussianBlur(image, (gaus_core_x, gaus_core_y), gaus_sigma_x, gaus_sigma_y)

                    case "erode":
                        eroz_x = int(meta.get("eroz_x"))
                        eroz_y = int(meta.get("eroz_y"))
                        eroz_iteration = int(meta.get("eroz_iteration"))

                        struct_elem = np.ones((eroz_x, eroz_y), np.uint8)
                        #  Применяем метод
                        update_image = cv2.erode(image, struct_elem, iterations=eroz_iteration)

                    case "dilatation":
                        dilatation_x = int(meta.get("dilatation_x"))
                        dilatation_y = int(meta.get("dilatation_y"))
                        dilatation_iteration = int(meta.get("dilatation_iteration"))

                        struct_elem = np.ones((dilatation_x, dilatation_y), np.uint8)
                        #  Применяем метод
                        update_image = cv2.dilate(image, struct_elem, iterations=dilatation_iteration)

                    case "bilat":
                        bilat_d = int(meta.get("bilat_d"))
                        bilat_color = int(meta.get("bilat_color"))
                        bilat_coord = int(meta.get("bilat_coord"))

                        #  Применяем метод
                        update_image = cv2.bilateralFilter(image, bilat_d, bilat_color, bilat_coord)

                metadata_id = uuid4()
                metadata = FileMetadata(
                    id=metadata_id,
                    meta=meta
                )

                await orm_uow.file_metadatas.insert(metadata)
                await orm_uow.commit()

                #  Получаем запись бд
                file = await orm_uow.files.get(id=file_id)

                update_image_id = uuid4()
                update_files_id.append(update_image_id)

                #  Создаем запись нового файла
                update_image_file = File(
                    id=update_image_id,
                    parent_id=file.id,
                    previous_file=file.previous_file if file.previous_file else None,
                    metadata_id=metadata_id
                )
                #  Создаем объект хранилища нового файла
                s3_model = S3Model(
                    bucket_name="sirius",
                    object_name=str(update_image_id),
                    data=io.BytesIO(update_image.tobytes()),
                    length=update_image.size,
                )
                self.storage_repository.insert(s3_model, None)

                await orm_uow.files.insert(update_image_file)

                #  Если родительское изображение чье-то предыдущее, то подменяем на новое
                next_file = await orm_uow.files.get(previous_file=file.id) if await orm_uow.files.get(previous_file=file.id) else None
                if next_file:
                    next_file.previous_file = update_image_file.id
                await orm_uow.commit()
        return update_files_id


@dataclass(kw_only=True, slots=True, frozen=True)
class GetPreviousFileListController(AsyncService):
    """Список файлов прошлой версии для отката изменений"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
        files_id: list,
    ):
        async with self.orm_unit_of_work as orm_uow:
            previous_file = []
            for file_id in files_id:
                file = await orm_uow.files.get(id=file_id)
                if file.parent_id:
                    previous_file.append(file.parent_id)
            return previous_file


@dataclass(kw_only=True, slots=True, frozen=True)
class SaveFilesController(AsyncService):
    """Пометка изображений готовыми к разметке или распознаванию"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
        self,
        files_id: list,
    ):
        async with self.orm_unit_of_work as orm_uow:
            for file_id in files_id:
                file = await orm_uow.files.get(id=file_id)
                file.is_final_image = True
                await orm_uow.commit()


@dataclass(kw_only=True, slots=True, frozen=True)
class CreateTrainDataController(AsyncService):
    """Создает обучающий файл"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
            self,
            data: list[dict],
            file_id: UUID,
    ):
        async with self.orm_unit_of_work as orm_uow:

            file_bytes = self.storage_repository.get(
                bucket_name="sirius", object_name=str(file_id)
            )
            #  Преобразуем в массив
            arr_image = np.reshape(np.frombuffer(file_bytes, dtype=np.uint8), (128, 1024))

            image = Image.fromarray(arr_image, 'L')
            out_img = io.BytesIO()
            image.save(out_img, format="png")
            out_img.seek(0)
            s3_model = S3Model(
                bucket_name="sirius",
                object_name=f"{str(file_id)}_train.jpg",
                data=out_img,
                length=-1,
            )

            self.storage_repository.insert(s3_model, None)

            with open(f"{str(file_id)}_train.txt", "w") as file:
                for data_row in data:
                    x1 = data_row.get("start").get("x")/1024
                    y1 = data_row.get("start").get("y")/128
                    x2 = data_row.get("end").get("x")/1024
                    y2 = data_row.get("end").get("y")/128
                    file.writelines(f"{data_row.get('class')} {x1} {y1} {x2} {y2}\n")

            with open(f"{str(file_id)}_train.txt", "rb") as file:
                s3_model = S3Model(
                    bucket_name="sirius",
                    object_name=f"{str(file_id)}_train.txt",
                    data=file,
                    length=-1,
                )
                self.storage_repository.insert(s3_model, None)
            os.remove(f"{str(file_id)}_train.txt")
            train_data = TrainData(
                id=uuid4(),
                file_id=str(file_id),
                jpg_name=f"{str(file_id)}_train.jpg",
                marking_name=f"{str(file_id)}_train.txt"
            )

            await orm_uow.train_data.insert(train_data)
            await orm_uow.commit()


@dataclass(kw_only=True, slots=True, frozen=True)
class FilePredictController(AsyncService):
    """Контроллер отправки на распрознавание изображения"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
            self,
            file_id: UUID,
    ):
        async with self.orm_unit_of_work as orm_uow:
            file_bytes = self.storage_repository.get(
                bucket_name="sirius", object_name=str(file_id)
            )
            #  Преобразуем в массив
            arr_image = np.reshape(np.frombuffer(file_bytes, dtype=np.uint8), (128, 1024))

            response = requests.post("http://localhost:8005/yolo/predict/predict_image", json=arr_image.tolist())
            return response.json()


@dataclass(kw_only=True, slots=True, frozen=True)
class FilePredictControllerTwo(AsyncService):
    """Контроллер отправки на распрознавание изображения"""

    orm_unit_of_work: FileUnitOfWork
    storage_repository: S3Repository

    async def __call__(
            self,
            file_id: UUID,
    ):
        async with self.orm_unit_of_work as orm_uow:
            file_bytes = self.storage_repository.get(
                bucket_name="sirius", object_name=str(file_id)
            )
            #  Преобразуем в массив
            arr_image = np.reshape(np.frombuffer(file_bytes, dtype=np.uint8), (128, 1024))

            response = requests.post("http://localhost:8005/yolo/predict/predict_image_2", json=arr_image.tolist())
            return response.json()