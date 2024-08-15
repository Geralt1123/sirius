from io import IOBase

from pydantic import BaseModel, ConfigDict


class S3Model(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    bucket_name: str
    object_name: str
    data: IOBase | None = None
    metadata: dict[str, str] | None = None
    length: int = -1
