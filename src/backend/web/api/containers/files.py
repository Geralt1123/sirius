from dependency_injector import containers, providers
from units_of_work import FileUnitOfWork
from web.api.controllers import (UploadFileController, DownloadFileController, GetNextFileController,
                                 GetPreviousFileController)


class FileControllerContainer(containers.DeclarativeContainer):
    """Заранее сконфигурированный контейнер для экспорта в Excel"""

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

    get_next_file_controller = providers.Factory(
        GetNextFileController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )

    get_previous_file_controller = providers.Factory(
        GetPreviousFileController,
        orm_unit_of_work=file_uow,
        storage_repository=storage.s3_repository,
    )
