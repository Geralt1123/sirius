import json
import logging
import os.path
from pathlib import Path

import structlog

base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logs_dir = Path(base_dir) / "logs"
logs_dir.mkdir(exist_ok=True)

MAX_BYTES = 1024 * 1024 * 3  # 3 Mb


def extract_from_record(_, __, event_dict):
    """достаем тред и ппроцесс"""
    record = event_dict["_record"]
    event_dict["thread_name"] = record.threadName
    event_dict["process_name"] = record.processName
    return event_dict


def formatter(*args, **kwargs):
    return json.dumps(*args, **kwargs, ensure_ascii=False)


LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(serializer=formatter),
        },
        "plain_console": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processors": [
                structlog.processors.TimeStamper(fmt="%H:%M:%S UTC", utc=True),
                extract_from_record,
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.dev.ConsoleRenderer(),
            ],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "plain_console",
        },
        "file_errors": {
            "level": logging.WARNING,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": logs_dir / "errors.log",
            "formatter": "json_formatter",
            "maxBytes": MAX_BYTES,
            "encoding": "utf-8",
        },
        "file_history": {
            "level": logging.DEBUG,
            "class": "logging.handlers.RotatingFileHandler",
            "mode": "w",
            "filename": logs_dir / "history.log",
            "formatter": "json_formatter",
            "maxBytes": MAX_BYTES,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "default": {
            "handlers": ["console", "file_errors", "file_history"],
            "level": "DEBUG",
        },
        "root": {
            "handlers": ["console", "file_errors", "file_history"],
            "level": "DEBUG",
        },
    },
}
