from typing import Any

from common.models.s3 import S3Model
from interfaces import AbstractSyncRepository
from boto3.resources.base import ServiceResource
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError, EndpointConnectionError
from common.exceptions import StorageException
from common.utils import TransferCallback
from datetime import timedelta


class S3Repository(AbstractSyncRepository):
    Model: S3Model
    _session: ServiceResource

    def __init__(
        self,
        session: ServiceResource,
        transfer_config: dict | None = None,
    ) -> None:
        super().__init__(session)
        transfer_config = transfer_config or {}
        self._transfer_config = TransferConfig(**transfer_config)

    def get(self, *filters, **named_filters) -> S3Model | None:
        """Получение элемента"""
        bucket_name = named_filters.get("bucket_name", "")
        object_name = named_filters.get("object_name", "")
        try:
            object = self._session.Bucket(bucket_name).Object(object_name).get()['Body'].read()
        except ClientError as e:
            raise StorageException(f"File download fails: {e}")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")
        return object

    def exists(self, instance: S3Model) -> bool:
        try:
            bucket = self._session.Bucket(instance.bucket_name)
            objects = set(map(lambda x: x.key, bucket.objects.filter(Prefix=instance.object_name)))
            return instance.object_name in objects
        except ClientError as e:
            raise StorageException(f"Check file exists fails: {e}")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")

    def remame(self, instance: S3Model, new_object_name: str):
        """Переименование элемента"""
        try:
            bucket = self._session.Bucket(instance.bucket_name)

            if self.exists(S3Model(bucket_name=instance.bucket_name, object_name=new_object_name)):
                raise StorageException(f"File with name {new_object_name} already exists")

            bucket.Object(new_object_name).copy_from(CopySource=f"{instance.bucket_name}/{instance.object_name}")
            bucket.Object(instance.object_name).delete()
        except ClientError as e:
            raise StorageException(f"File rename fails: {e}")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")

    def insert(self, instance: S3Model, transfer_callback: TransferCallback | None = None) -> None:
        """Вставка элемента"""
        extra_args = {"Metadata": instance.metadata} if instance.metadata else None

        transfer_callback = transfer_callback or TransferCallback(instance.length)

        try:
            self._session.Bucket(instance.bucket_name).upload_fileobj(
                instance.data,
                instance.object_name,
                ExtraArgs=extra_args,
                Callback=transfer_callback,
                Config=self._transfer_config,
            )
        except ClientError as e:
            raise StorageException(f"File upload fails: {e}")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")

    def delete(self, instance: S3Model) -> None:
        """Удаление элемента"""
        try:
            self._session.Bucket(instance.bucket_name).Object(instance.object_name).delete()
        except ClientError:
            raise StorageException("File deletion fails: file not found")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")

    def update(self, instance: S3Model, **update_fields) -> None:
        """Изменение элемента"""

        raise NotImplementedError

    def get_object_metadata(self, instance: S3Model) -> dict[str, Any]:
        """Получение метаданных объекта"""
        try:
            object_ = self._session.Bucket(instance.bucket_name).Object(instance.object_name).get()
        except ClientError:
            raise StorageException("File get metadata fails: file not found")
        except EndpointConnectionError:
            raise StorageException("Can't connect to storage")
        meaning_data = dict(
            content_type=object_["ContentType"],
            size=object_["ContentLength"],
            e_tag=object_["ETag"].strip('"'),
            **object_["Metadata"],
        )
        return meaning_data

    def get_object_link(self, instance: S3Model) -> str:
        """Получение ссылки на скачивание объекта"""
        method_access = "get_object"
        inner_link: str = self._session.meta.client.generate_presigned_url(
            method_access,
            Params={"Bucket": instance.bucket_name, "Key": instance.object_name},
            ExpiresIn=timedelta(minutes=1).seconds,
        )
        return inner_link
