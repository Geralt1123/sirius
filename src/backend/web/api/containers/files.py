from dependency_injector import containers, providers
from units_of_work import FileUnitOfWork
from web.api.controllers import (UploadFileController, DownloadFileController, GetFileListController,
                                 AddFilterController, GetPreviousFileListController, SaveFilesController,
                                 CreateTrainDataController, FilePredictController, FilePredictControllerTwo)


class FileControllerContainer(containers.DeclarativeContainer):
    """Заранее сконфигурированный контейнер"""

    config = providers.Configuration()
    database = providers.DependenciesContainer()
    storage = providers.DependenciesContainer()
    wiring_config = containers.WiringConfiguration(
        modules=["web.api.views.files"], auto_wire=False
    )

    file_uow = providers.Factory(FileUnitOfWork, session_factory=database.session_maker)

    upload_file_controller = providers.Factory(
        UploadFileController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    download_file_controller = providers.Factory(
        DownloadFileController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    get_final_file_list_controller = providers.Factory(
        GetFileListController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    gaus_controller = providers.Factory(
        AddFilterController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    get_previous_file_list_controller = providers.Factory(
        GetPreviousFileListController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    save_files_controller = providers.Factory(
        SaveFilesController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    create_train_data = providers.Factory(
        CreateTrainDataController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    file_predict_controller = providers.Factory(
        FilePredictController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    file_predict_controller_2 = providers.Factory(
        FilePredictControllerTwo,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )
