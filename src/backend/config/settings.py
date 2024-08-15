from abc import ABC

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvSettings(BaseSettings):
    """Базовый класс для чтения с поддержкой чтения переменных из окружения"""

    model_config = SettingsConfigDict(case_sensitive=True, env_file_encoding="utf-8")


class UvicornSettings(BaseEnvSettings):
    """параметры запуска сервера"""

    app: str = Field("config.asgi:application")
    port: int = Field(8000, validation_alias="PORT")
    host: str = Field("127.0.0.1", validation_alias="HOST")
    reload: bool = Field(False, validation_alias="DEBUG")
    use_colors: bool = Field(False, validation_alias="DEBUG")


class ApplicationSettings(BaseEnvSettings):
    """Параметры запуска приложения"""

    title: str = Field("SiriusService")
    debug: bool = Field(False, validation_alias="APP_DEBUG")
    prefix: str = Field("/sirius")


class DataBaseSessionSettings(BaseEnvSettings):
    """Параметры создания сессии БД"""

    autoflush: bool = Field(False, validation_alias="DB_AUTOFLUSH")
    autocommit: bool = Field(False, validation_alias="DB_AUTOCOMMIT")


class DataBaseSettings(BaseEnvSettings):
    """Параметры подключения к БД"""

    port: int = Field(5432, validation_alias="DB_PORT")
    host: str = Field("127.0.0.1", validation_alias="DB_HOST")
    user: str = Field("sirius", validation_alias="DB_USER")
    password: str = Field("sirius123", validation_alias="DB_PASS")
    database_name: str = Field("sirius", validation_alias="DB_NAME")
    schema_name: str = Field("sirius", validation_alias="DB_SCHEMA_NAME")

    def get_postgres_database_url(self) -> str:
        return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database_name}"


class StorageSettings(BaseEnvSettings, ABC):
    """Интерфейс настроек хранилища данных"""

    host: str
    port: int
    access_key: str
    secret_key: str
    secure: bool = True
    protocol: str = "http"

    def url(self) -> str:
        return f"{self.protocol}://{self.host}:{self.port}"


class S3Settings(StorageSettings):
    """Параметры подключения к хранилищу S3"""

    host: str = Field("127.0.0.1", validation_alias="S3_HOST")
    port: int = Field(9000, validation_alias="S3_PORT")
    access_key: str | None = Field(None, validation_alias="S3_ACCESS_KEY")
    secret_key: str | None = Field(None, validation_alias="S3_SECRET_KEY")
    secure: bool = Field(False, validation_alias="S3_SECURE")
    protocol: str = Field("http", validation_alias="S3_PROTOCOL")
    signature_version: str = Field("s3v4", validation_alias="S3_SIGNATURE_VERSION")


class JsonSerializerSettings(BaseEnvSettings):
    date_format: str = Field("%d.%m.%Y")


class S3TransferSettings(BaseEnvSettings):
    """Параметры передачи данных к хранилищу S3"""

    multipart_threshold: int = Field(8, validation_alias="S3_TRANSFER_MULTIPART_THRESHOLD")
    max_concurrency: int = Field(10, validation_alias="S3_TRANSFER_MAX_CONCURRENCY")
    multipart_chunksize: int = Field(8, validation_alias="S3_TRANSFER_MULTIPART_CHUNKSIZE")