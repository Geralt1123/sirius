from uuid import UUID, uuid4
from common.models.orm.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.orm import File


class FileMetadata(Base):
    __tablename__ = 'file_metadata'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    gaus_core_x: Mapped[int] = mapped_column(nullable=True)
    gaus_core_y: Mapped[int] = mapped_column(nullable=True)
    gaus_sigma_x: Mapped[int] = mapped_column(nullable=True)
    gaus_sigma_y: Mapped[int] = mapped_column(nullable=True)
    eroz_x: Mapped[int] = mapped_column(nullable=True)
    eroz_y: Mapped[int] = mapped_column(nullable=True)
    eroz_iteration: Mapped[int] = mapped_column(nullable=True)

    files: Mapped[list["File"]] = relationship(back_populates="file_metadata", lazy="select")
