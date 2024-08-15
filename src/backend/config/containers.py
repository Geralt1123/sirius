from boto3 import resource
from boto3.session import Config as S3Config
from common.repository import S3Repository
from dependency_injector import containers, providers
from common.serialization import JsonDeserializer, JsonSerializer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from config.config import (
    database_settings,
    database_session_settings,
    s3_config,
    s3_transfer_config,
    json_serializer_config,
)
from common.app_lifespan import ApplicationLifeSpan

from web.api.containers import ControllersContainer as ApiControllersContainer


class DataBaseContainer(containers.DeclarativeContainer):
    """Контейнер сессий базы данных"""

    config = providers.Configuration()
    json_serializer = providers.Dependency(instance_of=JsonSerializer)

    database_engine = providers.Callable(
        create_async_engine,
        url=database_settings.get_postgres_database_url(),
        json_serializer=json_serializer,
    )

    session_maker = providers.Singleton(
        async_sessionmaker, bind=database_engine.provided, **database_session_settings.model_dump()
    )


class StorageContainer(containers.DeclarativeContainer):
    """Контейнер хранилищ данных"""

    config = providers.Configuration()

    s3_resource = providers.Resource(
        resource,
        service_name="s3",
        endpoint_url=s3_config.url(),
        aws_access_key_id=s3_config.access_key,
        aws_secret_access_key=s3_config.secret_key,
        aws_session_token=None,
        config=S3Config(signature_version=s3_config.signature_version),
        verify=s3_config.secure,
    )

    s3_repository = providers.Singleton(
        S3Repository,
        session=s3_resource,
        transfer_config=s3_transfer_config.model_dump(),
    )


class ApplicationContainer(containers.DeclarativeContainer):
    """Общий контейнер сервиса"""

    config = providers.Configuration()

    json_serializer = providers.Singleton(JsonSerializer, **json_serializer_config.model_dump())
    json_deserializer = providers.Singleton(JsonDeserializer, **json_serializer_config.model_dump())

    database = providers.Container(DataBaseContainer, json_serializer=json_serializer)
    storage = providers.Container(StorageContainer)

    web = providers.Container(
        ApiControllersContainer,
        database=database,
        json_serializer=json_serializer,
        json_deserializer=json_deserializer,
        storage=storage,
    )
