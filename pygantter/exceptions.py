"""Exception types raised by PyGantter.

All errors that represent bad user input inherit from :class:`PyGantterError`
so the CLI can catch one type, print a clean message, and exit non-zero,
while unexpected bugs still surface as normal tracebacks.
"""

from __future__ import annotations


class PyGantterError(Exception):
    """Base class for all expected, user-facing PyGantter errors."""


class InputFormatError(PyGantterError):
    """Raised when an input file cannot be read or has an unsupported type."""


class ValidationError(PyGantterError):
    """Raised when task data is missing required fields or is inconsistent."""


class DateParseError(ValidationError):
    """Raised when a date value cannot be parsed."""


class DependencyError(ValidationError):
    """Raised for unknown dependency references or dependency cycles."""


class ThemeError(PyGantterError):
    """Raised when an unknown theme name is requested."""
