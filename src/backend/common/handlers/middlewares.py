import structlog
from common.exceptions import AuthorizationException, ControllerException
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response


class CatchExceptionMiddleware(BaseHTTPMiddleware):
    """Перехватывает ошибки, связанные с неправильным/некорректным запросом"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger = structlog.get_logger(request.url.path)
        try:
            return await call_next(request)
        except AuthorizationException as auth_ex:
            message = str(auth_ex)
            status_code = status.HTTP_401_UNAUTHORIZED
            logger.warning(message)
        except ControllerException as controller_ex:
            message = str(controller_ex)
            status_code = controller_ex.status_code
            logger.warning(message)
        except Exception as exception:
            logger.exception(str(exception))
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            message = "Внутренняя ошибка"

        return PlainTextResponse(message, status_code=status_code)


class RequestsLoggerMiddleware(BaseHTTPMiddleware):
    """Записывает все пришедшие запросы"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        logger = structlog.get_logger(request.url.path)
        logger.info(f"{request.method} {request.query_params}")
        return await call_next(request)
