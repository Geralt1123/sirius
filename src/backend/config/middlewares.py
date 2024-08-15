from typing import Any, Dict, List, Tuple


def get_middlewares() -> List[Tuple[Any, Dict]]:
    """Возвращает список из Middlewares+настроек к ним"""
    from common.handlers import CatchExceptionMiddleware, RequestsLoggerMiddleware

    return [(CatchExceptionMiddleware, {}), (RequestsLoggerMiddleware, {})]
