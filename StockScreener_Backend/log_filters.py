"""Logging filters module.

Provides custom logging filter classes that can be attached to
Python logging handlers.  In this project we use filters to
restrict which log levels are emitted by particular handlers.
"""

import logging


class FilterLevels(logging.Filter):
    """Filter that allows only specified log levels.

    Args:
        filter_levels (iterable[str] | None): Iterable of level names
            (e.g. ``"INFO"``, ``"ERROR"``) that should be allowed. If
            ``None`` the filter will block all records.
    """

    def __init__(self, filter_levels=None):
        super(FilterLevels, self).__init__()
        self._filter_levels = filter_levels

    def filter(self, record):
        """Determine if the provided log record should be processed.

        The logging system calls this method for each record; returning
        ``True`` allows the record to pass through, ``False`` drops it.

        Args:
            record (logging.LogRecord): The record to decide upon.

        Returns:
            bool: ``True`` if ``record.levelname`` is in the configured
            levels, otherwise ``False``.
        """
        if record.levelname in self._filter_levels:
            return True
        return False
