from uuid import UUID, uuid4
from common.models.orm.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.orm import File


class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    files: Mapped[list["File"]] = relationship(back_populates="file_metadata", lazy="select")
