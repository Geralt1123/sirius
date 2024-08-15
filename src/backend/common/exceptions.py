from starlette import status


class ControllerException(Exception):
    """Поведенческая ошибка контроллеров"""

    def __init__(self, message: str | None = None, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = status_code
        super().__init__(message)


class PermissionException(ControllerException):
    """Ошибки, связанные с доступом"""


class ServiceException(ControllerException):
    """Ошибки, возникающие в сервисах"""


class StorageException(ControllerException):
    """Ошибки, возникающие при работе с хранилищем"""


class AdapterException(ControllerException):  # authentication
    """Ошибки, возникающие в адаптерах"""


class AuthorizationException(Exception):
    """Ошибки авторизации"""
