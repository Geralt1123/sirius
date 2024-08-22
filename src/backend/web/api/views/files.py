from uuid import UUID

from fastapi import (
    APIRouter,
    Depends, Body, Query,
)
from dependency_injector.wiring import inject, Provide
from interfaces import Service
from web.api.containers import FileControllerContainer
from web.schemas.contracts import DataModel
from web.schemas.contracts.contracts import FileResponseModel, FileIdsResponseModel

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(path="/save_file", summary="Загрузка файла")
@inject
async def file_download(
    file: DataModel = Body(),
    controller: Service = Depends(Provide[FileControllerContainer.upload_file_controller])
):
    response = await controller(file)
    return response


@router.get(path="/get_file", summary="Скачивание файла", response_model=FileResponseModel)
@inject
async def file_get(
    file_id: UUID = Query(),
    controller: Service = Depends(Provide[FileControllerContainer.download_file_controller])
):
    response = await controller(file_id)
    return response


@router.get(path="/get_file_list", summary="Список файлов", response_model=FileResponseModel)
@inject
async def get_final_file_list(
    controller: Service = Depends(Provide[FileControllerContainer.get_final_file_list_controller])
):
    response = await controller()
    return response


@router.get(path="/add_method", summary="Фильтр гауса", response_model=FileIdsResponseModel)
@inject
async def gaus(
    files_id: list[UUID] = Query(),
    method: str = Query(),
    meta: dict = Body(),

    controller: Service = Depends(Provide[FileControllerContainer.gaus_controller])
):
    response = await controller(files_id, method, meta)
    return response


@router.get(path="/previous_file_list", summary="Фильтр гауса", response_model=FileIdsResponseModel)
@inject
async def get_previous_file_list(
    files_id: list[UUID] = Query(),
    controller: Service = Depends(Provide[FileControllerContainer.get_previous_file_list_controller])
):
    response = await controller(files_id)
    return response


@router.get(path="/save_files", summary="Пометка изображений как финальное")
@inject
async def save_files(
    files_id: list[UUID] = Query(),
    controller: Service = Depends(Provide[FileControllerContainer.save_files_controller])
):
    await controller(files_id)
