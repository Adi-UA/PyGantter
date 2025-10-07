import pytest

from pygantter.logging import get_logger, setup_logger


def test_setup_and_get_logger(caplog):
    logger = setup_logger("test_logger")
    logger.info("Test info message")
    log = get_logger("test_logger")
    log.error("Test error message")
    assert logger.name == "test_logger"
    assert log.name == "test_logger"
    assert logger.name == "test_logger"
    assert log.name == "test_logger"
