from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from common.models.orm.base import Base
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.orm import FileMetadata, TrainData


class File(Base):
    __tablename__ = 'file'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    parent_id: Mapped[UUID] = mapped_column(nullable=True, comment="id родительского файла")

    @declared_attr
    def metadata_id(self) -> Mapped[UUID]:
        return mapped_column(
            ForeignKey(f"{self._schema_name}.file_metadata.id"), nullable=True, comment="метадата"
        )

    is_final_image: Mapped[bool] = mapped_column(nullable=True, comment="финальное изображение")
    previous_file: Mapped[UUID] = mapped_column(nullable=True, comment="предыдущее изображение")

    file_metadata: Mapped["FileMetadata"] = relationship(back_populates="files", lazy="select")
    train_data: Mapped[list["TrainData"]] = relationship(back_populates="file", lazy="select")
