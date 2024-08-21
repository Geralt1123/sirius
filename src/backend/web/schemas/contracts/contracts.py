from uuid import UUID

from pydantic import RootModel, Field, BaseModel


class DataModel(RootModel):
    root: list[list[float]]


class IdModel(BaseModel):
    id: UUID | None = Field(default=None)


class FileResponseModel(RootModel, arbitrary_types_allowed=True):
    root: list[list[int]]


class FileIdsResponseModel(RootModel):
    root: list[UUID] | None
