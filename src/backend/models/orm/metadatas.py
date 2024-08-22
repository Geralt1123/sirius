from uuid import UUID, uuid4

from sqlalchemy.dialects.postgresql import JSONB

from common.models.orm.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.orm import File


class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    meta: Mapped[dict] = mapped_column(type_=JSONB, nullable=True)

    files: Mapped[list["File"]] = relationship(back_populates="file_metadata", lazy="select")
