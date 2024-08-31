from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from common.models.orm.base import Base
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.orm import File


class TrainData(Base):
    __tablename__ = 'train_data'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    @declared_attr
    def file_id(self) -> Mapped[UUID]:
        return mapped_column(
            ForeignKey(f"{self._schema_name}.file.id"), nullable=True, comment="файл"
        )

    jpg_name: Mapped[str] = mapped_column(nullable=True, comment="название jpg фала")
    marking_name: Mapped[str] = mapped_column(nullable=True, comment="название jpg фала")

    file: Mapped["File"] = relationship(back_populates="train_data", lazy="select")
