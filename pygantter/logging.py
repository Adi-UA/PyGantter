"""Logging setup for PyGantter."""

from __future__ import annotations

import logging

_DEFAULT_NAME = "pygantter"


def setup_logger(name: str = _DEFAULT_NAME, level: int = logging.INFO) -> logging.Logger:
    """Return a configured logger, attaching a stream handler once."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
            )
        )
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return an existing logger by name, defaulting to the package logger."""
    return logging.getLogger(name or _DEFAULT_NAME)
