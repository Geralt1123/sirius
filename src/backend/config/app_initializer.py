import asyncio

from config.config import application_config
from config.containers import ApplicationContainer
from fastapi import FastAPI


def initialize_routers(application: FastAPI) -> None:
    from config.routers import get_routers

    for router in get_routers():
        application.include_router(router, prefix=application_config.prefix)


def initialize_containers(container: ApplicationContainer) -> None:
    for sub_container in container.web.sub_containers().values():
        sub_container.wire()


def get_fastapi_application(container=ApplicationContainer()) -> FastAPI:
    """Сборка приложения"""

    initialize_containers(container)
    lifespan = None

    application: FastAPI = FastAPI(**application_config.model_dump(), lifespan=lifespan)
    initialize_routers(application)
    initialize_middlewares(application)

    initialize_logger()
    return application


def initialize_middlewares(application: FastAPI) -> None:
    from config.middlewares import get_middlewares

    for middleware, options in get_middlewares():
        application.add_middleware(middleware, **options)


def initialize_logger():
    import logging.config

    import structlog
    from common.logger import LOGGER_CONFIG

    logging.config.dictConfig(LOGGER_CONFIG)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),  # %H:%M:%S UTC
            structlog.stdlib.add_logger_name,  # Add the name of the logger to event dict.
            structlog.stdlib.add_log_level,  # Добавляет уровень журнала в словарь событий под ключом level.
            structlog.stdlib.PositionalArgumentsFormatter(),  # Perform %-style formatting.
            structlog.processors.StackInfoRenderer(),  # render the current stack trace in the "stack" key.
            structlog.processors.format_exc_info,  # вставялет стек вызовов в сообщение
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
