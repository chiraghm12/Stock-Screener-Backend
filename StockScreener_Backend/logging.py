"""Logging configuration helpers.

This module builds a comprehensive ``LOGGING`` dictionary that can be
passed to :func:`django.utils.log.dictConfig` or the standard library
``logging.config.dictConfig`` to establish file-based and console
logging for the project.  It constructs handlers for each supported
severity level and uses a custom ``FilterLevels`` filter to route
messages to separate files.

Typical usage::

    from .logging import LOGGING
    logging.config.dictConfig(LOGGING)
"""

import os
from datetime import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGGING_DIR = os.path.join(BASE_DIR, "stock_screener_logs")
os.makedirs(LOGGING_DIR, exist_ok=True)
INTERVAL = 1
BACKUP_COUNT = 5
LOGGING_VERSION = 1

Filters = {
    "filter_info_level": {
        "()": "StockScreener_Backend.log_filters.FilterLevels",
        "filter_levels": ["INFO"],
    },
    "filter_error_level": {
        "()": "StockScreener_Backend.log_filters.FilterLevels",
        "filter_levels": ["ERROR"],
    },
    "filter_debug_level": {
        "()": "StockScreener_Backend.log_filters.FilterLevels",
        "filter_levels": ["DEBUG"],
    },
    "filter_warning_level": {
        "()": "StockScreener_Backend.log_filters.FilterLevels",
        "filter_levels": ["WARNING"],
    },
}

Formatter = {
    "verbose": {
        "format": "{levelname} {asctime} [{pathname}:{module}:{funcName}:{lineno}] {message}",
        "datefmt": "%Y-%m-%d %H:%M:%S",
        "style": "{",
    },
    "simple": {
        "format": "{levelname} {message}",
        "style": "{",
    },
}

log_types = ["stock_screener"]


def get_logger(filter_name, filename):
    """Return a handler configuration dictionary.

    The returned dict is suitable for use in the ``handlers`` section of a
    :data:`LOGGING` configuration.  It sets up a
    :class:`concurrent_log_handler.ConcurrentTimedRotatingFileHandler`
    that rotates logs at midnight, keeps a fixed number of backups, and
    applies the provided filter to restrict records by level.

    Args:
        filter_name (str): Key of a filter defined in :data:`Filters`.
        filename (str): Base name of the file where logs should be written.

    Returns:
        dict: Handler configuration dictionary.
    """

    return {
        "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
        "formatter": "verbose",
        "filters": [filter_name],
        "filename": os.path.join(LOGGING_DIR, filename),
        "when": "midnight",
        "interval": INTERVAL,
        "backupCount": BACKUP_COUNT,  # number of backup files to keep
        "encoding": None,
        "delay": True,
        "utc": True,
        "errors": None,
        "atTime": time(0, 0),
    }


handlers = {}
for log_type in log_types:
    handlers[f"{log_type}_info_logger"] = get_logger(
        "filter_info_level", f"{log_type}_info.log"
    )

    handlers[f"{log_type}_error_logger"] = get_logger(
        "filter_error_level", f"{log_type}_error.log"
    )

    handlers[f"{log_type}_warning_logger"] = get_logger(
        "filter_warning_level", f"{log_type}_warning.log"
    )

    handlers[f"{log_type}_debug_logger"] = get_logger(
        "filter_debug_level", f"{log_type}_debug.log"
    )

handlers["console"] = {
    "class": "logging.StreamHandler",
    "level": "DEBUG",
    "formatter": "simple",
}

loggers = {}
for log_type in log_types:
    loggers[f"{log_type}_logger"] = {
        "handlers": [
            f"{log_type}_info_logger",
            f"{log_type}_error_logger",
            f"{log_type}_warning_logger",
            f"{log_type}_debug_logger",
            "console",
        ],
        "level": "DEBUG",
        "propagate": True,
    }

LOGGING = {
    "version": LOGGING_VERSION,
    "disable_existing_loggers": False,
    "filters": Filters,
    "formatters": Formatter,
    "handlers": handlers,
    "loggers": loggers,
}
