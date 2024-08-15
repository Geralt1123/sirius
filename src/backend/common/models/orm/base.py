from config import database_settings
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Базовый класс моделей SQLAlchemy"""

    @declared_attr
    def _schema_name(self):
        return database_settings.schema_name

    @declared_attr
    def __table_args__(self):
        return {"schema": self._schema_name}
